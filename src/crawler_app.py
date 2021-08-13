from typing import List
from .adapter import adapter
from .crawler.toko import req_toko, req_toko_stat, parse_toko
from .crawler.discover import DiscoverProduct, Categ, ProductItem
from .crawler.product import ProductChuck
import requests

discover = DiscoverProduct()

@adapter.register("crawler_q", publish_exchange="crawler_rpc")
def get_info_toko(username):
    shop = req_toko(username)
    stat = req_toko_stat(shop['shopCore']['shopID'])

    hasil = parse_toko(shop, stat)
    return hasil

@adapter.register("crawler_q", publish_exchange="crawler_rpc")
def get_products_categ(categ: Categ):
    try:

        pitems: List[ProductItem] = list(discover.req(categ))
        urls = list(map(lambda x: x.url, pitems))

        chunk = ProductChuck(urls)
        hasil = list(chunk.get())

        return hasil

    except Exception as e:
        print(e)
    
        return []

@adapter.register("crawler_q", publish_exchange="crawler_rpc")
def test():
    return { "test": "test" }


if __name__ == '__main__':
    hasil = get_products_categ(discover.categories[0])
    print(hasil)


