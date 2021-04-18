from typing import TypedDict, Callable
import uuid
import traceback

import pika
import dill
import requests
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))


class ReqPayload(TypedDict):
    funcname: str
    arg: list
    kwarg: dict


class Tasker:
    func: Callable
    channel: BlockingChannel
    routing_name: str
    cor_id: str
    name: str
    def __init__(self, name: str, connection: BlockingConnection, channel: BlockingChannel, func: Callable, routing_name: str):
        self.connection = connection
        self.func = func
        self.routing_name = routing_name
        self.channel = channel
        self.name = name

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            self.worker_response,
            self.callback_queue,
            no_ack=True)

    def __call__(self, *arg, **kwarg):
        return self.func(*arg, **kwarg)

    def worker_response(self, ch: BlockingChannel, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = dill.loads(body)
        else:
            print('not corelation')

    def execute(self, *arg, **kwarg):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        req: ReqPayload = {
            'funcname': self.name,
            'arg': arg,
            'kwarg': kwarg
        }

        rawreq = dill.dumps(req)
        
        self.channel.basic_publish(
            exchange='',
            routing_key=self.routing_name,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=rawreq)

        while self.response is None:
            self.connection.process_data_events()

        return self.response


class Worker:
    connection: BlockingConnection
    channel: BlockingChannel
    queue_name: str
    func_list: dict

    def __init__(self, connection: BlockingConnection, queue_name: str):
        self.connection = connection
        self.queue_name = queue_name
        self.channel = connection.channel()
        self.channel.queue_declare(queue=self.queue_name)
        self.func_list = {}

    def execute_request(self, request: ReqPayload):
        fname = request['funcname']
        arg = request['arg']
        kwarg = request['kwarg']

        func = self.func_list.get(fname)
        if(callable(func)):
            try:
                print('[ processing ] {}'.format(fname))
                return func(*arg, **kwarg)
            except Exception:
                traceback.print_exc()

    def on_request(self, channel: BlockingChannel, method, props, body):
        request = dill.loads(body)
        response = self.execute_request(request)

        channel.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=dill.dumps(response))
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def register(self, func)-> Tasker:
        name = func.__name__
        if self.func_list.get(name, None):
            raise Exception('fungsi sudah diregist')
        
        task: Tasker = Tasker(name, self.connection, self.channel, func, self.queue_name)

        self.func_list[name] = func
        return task

    def start(self, prefetch_count: int = 1):
        self.channel.basic_qos(prefetch_count=prefetch_count)
        self.channel.basic_consume(self.on_request, self.queue_name, no_ack=False)

        print(" [x] RPC Worker started")
        self.channel.start_consuming()
