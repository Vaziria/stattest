import pika
from mause_rpc.client import get_client

rpc_queue = 'rpc.queue'
client = get_client(rpc_queue, pika.ConnectionParameters(host='localhost'))

for c in range(0, 200):
    print(c)
    print(client.hello('mark'))
    print(client.divide(5, 2))
