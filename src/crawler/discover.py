import requests
from ..utils.persist import Persist

DEFAULT_HEADER = {

}

class ProductDiscover:
    urls = []
    limit: int
    def run(self, limit: int = 1000):
        self.limit = limit
    

    def add_url(self, url: str):
        self.urls = self.urls[:self.limit]
        self.urls.append(url)

    def is_product_url(self, url: str):
        print(url)

    


