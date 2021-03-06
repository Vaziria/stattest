import sys
import asyncio
import requests
import tornado.ioloop
from src.core.adapter import TornadoAdapter
from tornado import gen

RABBIT_URI = "amqp://localhost:5672/"


def calc_fib(message):
    req = requests.get('https://shopee.co.id')
    return req.status_code


@gen.coroutine
def handle_message(logger, message):
    logger.info("Fibonacci calc request {}".format(message))
    res = 'asdasdasdasdasd'
    logger.info("Fibonacci calc result {}".format(res))
    return res


@gen.coroutine
def handle_test(logger, message):
    logger.info(f"Got message: {message}")
    logger.info("Test succeeded!")


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    print("Creating Rabbit Listener")
    configuration = dict(
        receive=dict(
            incoming_1=dict(
                exchange="test_rpc",
                exchange_type="direct",
                routing_key="fib_calc",
                queue="fib_calc_q",
                durable=True,
                auto_delete=False,
                prefetch_count=1
            ),
            incoming_2=dict(
                exchange="test_2",
                exchange_type="direct",
                routing_key="test_2",
                queue="test_2",
                durable=True,
                auto_delete=False,
                prefetch_count=1
            )
        ),
        publish=dict(
            outgoing=dict(
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
    # Using Tornado IO Loop
    io_loop = tornado.ioloop.IOLoop.current()
    rabbit_connection = TornadoAdapter(rabbitmq_url=RABBIT_URI, configuration=configuration, io_loop=io_loop)
    rabbit_connection.receive(handler=handle_message, queue=configuration["receive"]["incoming_1"]["queue"])
    rabbit_connection.receive(handler=handle_test, queue=configuration["receive"]["incoming_2"]["queue"])
    io_loop.start()