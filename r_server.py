import pika
import requests
from src.distrib_core import Worker

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
crawling = Worker(connection, queue_name = 'crawler')


@crawling.register
def req_ip():
    req = requests.get('http://ifconfig.me')
    return {
        'body': req.text,
        'code': req.status_code
    }

@crawling.register
def req_shopee():
    req = requests.get('https://shopee.co.id/')
    return {
        'body': req.text[:100],
        'code': req.status_code
    }

if __name__ == '__main__':
    crawling.start()
    print(req_ip())