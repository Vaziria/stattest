import time
from test_server import io_loop, test


def test_using_distributed(benchmark):
    def run():
        io_loop.run_until_complete(test())
    benchmark(run)