import time
from locust import User, HttpUser, task, between
import pika
from src.distrib_core import Worker

class GrabClient:
    def __getattr__(self, name):
        def func():
            pass

        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                total_time = int((time.time() - start_time) * 1000)
                self._locust_environment.events.request_failure.fire(
                    request_type="distributed", name=name, response_time=total_time, exception=e
                )
            else:
                total_time = int((time.time() - start_time) * 1000)
                self._locust_environment.events.request_success.fire(
                    request_type="distributed", name=name, response_time=total_time, response_length=0
                )
                # In this example, I've hardcoded response_length=0. If we would want the response length to be
                # reported correctly in the statistics, we would probably need to hook in at a lower level

        return wrapper

class GrabUser(User):
    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        conparam = pika.ConnectionParameters(host='localhost')
        connection = pika.BlockingConnection(conparam)
        crawling = Worker(connection, queue_name = 'crawler')

        self.client = GrabClient()
        self.client._locust_environment = self.environment


class QuickstartUser(GrabUser):
    wait_time = between(1, 2.5)

    @task
    def crawl_ip(self):
        self.client.req_ip.execute()

    @task
    def crawl_shopee(self):
        self.client.req_shopee.execute()