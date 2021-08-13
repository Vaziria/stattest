import asyncio
import requests
import sys
import os

from .core.adapter import TornadoAdapter

RABBIT_URI = os.environ.get('RABBIT_URI', "amqp://localhost:5672/")

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

configuration = dict(
    publish=dict(
        outgoing_1=dict(
            exchange="crawler_rpc",
            exchange_type="direct",
            routing_key="crawler_out",
            queue="crawler_out_q",
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
            exchange="crawler_server",
            exchange_type="direct",
            routing_key="crawler",
            queue="crawler_q",
            durable=True,
            auto_delete=False,
            prefetch_count=1
        )
    )
)




io_loop = asyncio.get_event_loop()
adapter = TornadoAdapter(rabbitmq_url=RABBIT_URI, configuration=configuration, io_loop=io_loop)