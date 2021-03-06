import sys
import asyncio

import tornado.ioloop
import tornado.web
from tornado import gen
from src.core.adapter import TornadoAdapter


RABBIT_URI = "amqp://localhost:5672/"


class MainHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        self.application.rabbit_adapter.publish(body="Second test message", exchange="test_2")
        self.write("Fibonacci calculator: Just pass num=<SOME-NUMBER> at URL Parameters | ")
        num = self.get_argument("num", None, True)
        self.write("Calculating Fibonacci for " + str(num))
        # Send RabbitMQ message to the Calculator Microservice and wait for result
        res = yield self.application.rabbit_adapter.rpc(
            body=num, receive_queue="fib_server_q", publish_exchange="test_rpc", timeout=200, ttl=200)
        self.write(" | Result: {}".format(int(res)))
        self.application.rabbit_adapter.logger.info("Result: {}".format(int(res)))


def make_fibonacci_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


def create_adapter():
    configuration = dict(
        publish=dict(
            outgoing_1=dict(
                exchange="test_rpc",
                exchange_type="direct",
                routing_key="fib_calc",
                queue="fib_calc_q",
                durable=True,
                auto_delete=False,
                prefetch_count=1
            ),
            outgoing_2=dict(
                exchange="test_2",
                exchange_type="direct",
                routing_key="test_2",
                queue="test_2",
                durable=True,
                auto_delete=False,
                prefetch_count=1
            )
        ),
        receive=dict(
            incoming=dict(
                exchange="test_server",
                exchange_type="direct",
                routing_key="fib_server",
                queue="fib_server_q",
                durable=True,
                auto_delete=False,
                prefetch_count=1
            )
        )
    )
    # Using AsyncIO IO Loop
    io_loop = asyncio.get_event_loop()
    return TornadoAdapter(rabbitmq_url=RABBIT_URI, configuration=configuration, io_loop=io_loop)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Create Fibonacci web app
    app = make_fibonacci_app()
    app.listen(8888)
    configuration = dict(
        publish=dict(
            outgoing_1=dict(
                exchange="test_rpc",
                exchange_type="direct",
                routing_key="fib_calc",
                queue="fib_calc_q",
                durable=True,
                auto_delete=False,
                prefetch_count=1
            ),
            outgoing_2=dict(
                exchange="test_2",
                exchange_type="direct",
                routing_key="test_2",
                queue="test_2",
                durable=True,
                auto_delete=False,
                prefetch_count=1
            )
        ),
        receive=dict(
            incoming=dict(
                exchange="test_server",
                exchange_type="direct",
                routing_key="fib_server",
                queue="fib_server_q",
                durable=True,
                auto_delete=False,
                prefetch_count=1
            )
        )
    )
    # Using AsyncIO IO Loop
    io_loop = asyncio.get_event_loop()
    app.rabbit_adapter = TornadoAdapter(rabbitmq_url=RABBIT_URI, configuration=configuration, io_loop=io_loop)
    app.rabbit_adapter.publish(body="First second test message", exchange="test_2")
    io_loop.run_forever()