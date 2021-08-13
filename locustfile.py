import time
import asyncio
from locust import HttpUser, task, between
from src.crawler_app import get_info_toko
class QuickstartUser(HttpUser):
    wait_time = between(1, 2.5)


    @task(3)
    def view_items(self):
        for _ in range(10):
            self.client.get(f"/", name="test")