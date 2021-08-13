import asyncio
from src.adapter import adapter, configuration, io_loop
from src import crawler_app


async def test():
    # await adapter.publish(body="First second test message", exchange="test_2")
    events = []
    for _ in range(0, 10):
        future = crawler_app.get_info_toko.execute('diskonlaptop')
        events.append(future)
    
    hasil = await asyncio.gather(*events)
    print(hasil)
io_loop.run_until_complete(test())
