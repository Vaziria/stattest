import time
from locust import HttpUser, task, between

class QuickstartUser(HttpUser):
    wait_time = between(1, 2.5)


    @task(3)
    def view_items(self):
        for _ in range(10):
            self.client.get(f"/?num=7", name="/item")