import asyncio
import requests
import sys

from src.core.adapter import TornadoAdapter

RABBIT_URI = "amqp://localhost:5672/"

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

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

io_loop = asyncio.get_event_loop()
adapter = TornadoAdapter(rabbitmq_url=RABBIT_URI, configuration=configuration, io_loop=io_loop)

@adapter.register("fib_server_q", publish_exchange="test_rpc")
def crawl_shopee():
    req = requests.get('https://tokopedia.com')
    return req

if __name__ == '__main__':
    async def test():
        # await adapter.publish(body="First second test message", exchange="test_2")
        events = []
        for _ in range(0, 10):
            future = crawl_shopee.execute('diskonlaptop')
            events.append(future)
        
        hasil = await asyncio.gather(*events)
        print(hasil)
    io_loop.run_until_complete(test())
# asyncio.gather(*data)