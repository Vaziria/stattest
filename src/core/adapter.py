from typing import TypedDict
import uuid
import sys

from pika import BasicProperties
from pika import URLParameters, ConnectionParameters
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.concurrent import Future

from .async_connection import AsyncConnection
from .channel_configuration import ChannelConfiguration
from .task_adapter import TaskAdapter
from .tasker import Tasker, ReqPayload

from vazutils.logger import Logger

logger = Logger(__name__)

class QueueConfig(TypedDict):
    exchange: str
    exchange_type: str
    routing_key: str
    queue: str
    durable: bool
    auto_delete: bool
    prefetch_count: int

class ConfigPublish(TypedDict):
    outgoing_1: QueueConfig
    outgoing_2: QueueConfig

class ConfigReceive(TypedDict):
    incoming: QueueConfig

class Config(TypedDict):
    publish: ConfigPublish
    receive: ConfigReceive


class TornadoAdapter(TaskAdapter):

    logger = logger
    pub_connection: AsyncConnection
    rcv_connection: AsyncConnection

    def __init__(self, rabbitmq_url, configuration: Config, io_loop=None):
        super().__init__()

        self._parameter = ConnectionParameters("127.0.0.1") \
            if rabbitmq_url in ["localhost", "127.0.0.1"] else URLParameters(rabbitmq_url)
        if io_loop is None:
            io_loop = IOLoop.current()
        self.io_loop = io_loop
        self.configuration = configuration

        self.pub_connection = AsyncConnection(rabbitmq_url, io_loop)

        configpub = configuration["publish"].values()
        self.pub_channels = self.create_channel('exchange', self.pub_connection, *configpub)

        self.rcv_connection = AsyncConnection(rabbitmq_url, io_loop)

        configrcv = configuration["receive"].values()
        self.rcv_channels = self.create_channel('queue', self.rcv_connection, *configrcv)
        # print(self.rcv_channels)

        self._rpc_corr_id_dict = dict()

    def create_channel(self, key, connection: AsyncConnection, *configs: QueueConfig)-> dict:
        channels = {}

        for config in configs:
            channel = ChannelConfiguration(connection, self.io_loop, **config)
            channels[config[key]] = channel

        return channels

    def emitter(self, req: ReqPayload, *arg, **kwarg):
        return self.rpc(req, *arg, **kwarg)

    @gen.coroutine
    def publish(self, body, exchange, properties=None,  mandatory=True):
        """
        Publish a message. Creates a brand new channel in the first time, then uses the existing channel onwards.
        :param body: message
        :param exchange: The exchange to publish to
        :param properties: RabbitMQ message properties
        :param mandatory: RabbitMQ publish mandatory param
        """
        body = self.serialize(body)

        self.logger.info("Trying to publish message")
        if properties is None:
            properties = BasicProperties(delivery_mode=2)

        publish_channel = self.pub_channels.get(exchange)
        if publish_channel is None:
            self.logger.error("There is not publisher for the given exchange")

        try:
            yield publish_channel.publish(body, properties=properties, mandatory=mandatory)
        except Exception:
            self.logger.exception(f"Failed to publish message")
            raise Exception("Failed to publish message")

    @gen.coroutine
    def receive(self, queue, no_ack=False):
        """
        Receive messages. Creates a brand new channel in the first time, then uses the existing channel onwards.
        The first time it declares exchange and queue, then bind the queue to the particular exchange with routing key.
        If received properties is not none, it publishes result back to `reply_to` queue.
        :param handler: message handler
        :type handler gen.coroutine def fn(logger, body)
        :param queue: The queue to consume from
        :param no_ack: whether to ack
        """
        receive_channel = self.pub_channels.get(queue)
        if receive_channel is None:
            print(self.pub_channels)
            self.logger.error("There is not receiver for the given queue")

        try:
            yield receive_channel.consume(self._on_message, no_ack=no_ack)
        except Exception as e:
            self.logger.exception(f"Failed to receive message. {str(e)}")
            raise Exception("Failed to receive message")

    def _on_message(self, unused_channel, basic_deliver, properties, body):
        body = self.deserialize(body)
        self.logger.info("Received a new message")
        self.io_loop.call_later(0.01, self._process_message, unused_channel, basic_deliver, properties, body)

    @gen.coroutine
    def _process_message(self, unused_channel, basic_deliver, properties, body: ReqPayload):
        handler = self.get_handler(body)
        try:
            result = handler(*body['arg'], **body['kwarg'])
            result = self.serialize(result)

            self.logger.info(f"[ {properties.correlation_id} ] Message has been processed successfully")
            if properties is not None and properties.reply_to is not None:
                self.logger.info(f"[ {properties.reply_to} ][ {properties.correlation_id} ] sending result")
                publish_channel = list(self.rcv_channels.values())[0]
                yield publish_channel.publish(properties=BasicProperties(correlation_id=properties.correlation_id),
                                              body=result,
                                              mandatory=False,
                                              reply_to=properties.reply_to
                                              )

        except Exception:
            self.logger.exception("Failed to handle received message.")
            raise Exception("Failed to handle received message.")
        finally:
            unused_channel.basic_ack(basic_deliver.delivery_tag)

    @gen.coroutine
    def rpc(self, body, receive_queue, publish_exchange, timeout, ttl):

        receive_channel = self.rcv_channels.get(receive_queue)
        if receive_channel is None:
            self.logger.error("There is not receiver for the given queue")

        self.logger.info(f"Preparing to rpc call. Publish exchange: {publish_exchange}; Receive queue: {receive_queue}")
        yield receive_channel.consume(self._rpc_callback_process)

        correlation_id = str(uuid.uuid1())
        self.logger.info(f"Starting rpc calling correlation id: {correlation_id}")
        if correlation_id in self._rpc_corr_id_dict:
            self.logger.warning(f"Correlation id exists before calling. {correlation_id}")
            del self._rpc_corr_id_dict[correlation_id]

        self._rpc_corr_id_dict[correlation_id] = Future()
        properties = BasicProperties(
            correlation_id=correlation_id, reply_to=receive_queue, expiration=str(ttl*1000))
        yield self.publish(body, publish_exchange, properties=properties, mandatory=True)
        self.logger.info(f"RPC message has been sent. {correlation_id}")
        result = yield self._wait_result(correlation_id, timeout)
        if correlation_id in self._rpc_corr_id_dict:
            del self._rpc_corr_id_dict[correlation_id]
        self.logger.info(f"RPC message gets response. {correlation_id}")
        return result

    def _rpc_callback_process(self, unused_channel, basic_deliver, properties, body):
        
        if properties.correlation_id in self._rpc_corr_id_dict:
            body = self.deserialize(body)
            self._rpc_corr_id_dict[properties.correlation_id].set_result(body)
        else:
            self.logger.warning(f"RPC get non exist response. Correlation id: {properties.correlation_id}")
        unused_channel.basic_ack(basic_deliver.delivery_tag)
        
        self.logger.info(f"[ {properties.correlation_id} ] acknowledge" )

    def _wait_result(self, corr_id, timeout=None):
        self.logger.info(f"Beginning waiting for result. {corr_id}")
        future = self._rpc_corr_id_dict[corr_id]

        def on_timeout():
            if corr_id in self._rpc_corr_id_dict:
                self.logger.error(f"RPC timeout. Correlation id: {corr_id}")
                del self._rpc_corr_id_dict[corr_id]
                future.set_exception(Exception(f'RPC timeout. Correlation id: {corr_id}'))

        if timeout is not None:
            self.io_loop.call_later(timeout, on_timeout)
        return future

    def status_check(self):
        return self.rcv_connection.status_ok and self.pub_connection.status_ok
