import pika
import time
from mause_rpc.server import Server

rpc_queue = 'rpc.queue'
server = Server(rpc_queue, pika.ConnectionParameters(host='localhost'))


@server.register
def hello(name: str) -> str:
    return 'hello ' + name


@server.register('divide')
def div(a: int, b: int) -> float:
    if b == 0:
        raise ZeroDivisionError()
    return a / b


if __name__ == '__main__':
    server.serve()