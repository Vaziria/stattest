import requests
from typing import List
import json
from urllib.parse import urlencode

from tokopedia_client.category_api import CategoryApi
from tokopedia_client.graphql.payload import generate_payload, _gql_uri

from ..error.api_error import ApiExcetion
from ..utils.persist import Persist

DEFAULT_HEADER = {
    'Content-Type': 'application/json',
    'Origin': 'https://www.tokopedia.com',
    'Referer': 'https://www.tokopedia.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'X-Source': 'tokopedia-lite',
    'X-Tkpd-Lite-Service': 'zeus'
}

class Categ:
    finished: bool
    last_page: int
    name: str
    # identifier: str
    id: int
    count: int


class ShopItem:
    id: int
    name: str
    url: str

    def __init__(self, id: int, name: str, url: str):
        self.id = id
        self.name = name
        self.url = url

class ProductItem:
    
    shop: ShopItem
    id: int
    url: str
    productkey: str
    shopdomain: str

    def __init__(self, id: int, url: str, shop: ShopItem, productkey: str, shopdomain: str):
        self.id = id
        self.url = url
        self.shop = shop
        self.productkey = productkey
        self.shopdomain = shopdomain
        
class DiscoverProduct(Persist):
    loc = 'cache/discover_product'
    categories: list
    categApi: CategoryApi
    limit_per_page = 40


    def __init__(self):
        self.categApi = CategoryApi()
        
        self.categories = []

        if self.categories:
            self.load_obj()
            
        else:
            self.get_categories()

    def get_categories(self):
        hasil = self.categApi.gql_categories()

        rawCategs = hasil['data']['categoryAllListLite']['categories']

        hasil = []

        for categ in rawCategs:
            hasil.extend(self.categApi.inspectChild(categ))
        
        for data in hasil:
            cat = Categ()
            cat.finished = False
            cat.id = data['id']
            cat.name = data['name']
            cat.last_page = 0

            self.categories.append(cat)
        
        self.save_obj()

    def create_payload(self, categ: Categ):
        page = categ.last_page
        page = int(page)

        start = page * self.limit_per_page

        params = {
            'page': page,
            'ob': '',
            # 'identifier': categ.get('identifier'),
            'sc': categ.id,
            'user_id': '0',
            'rows': self.limit_per_page,
            'start': start,
            'source': 'directory',
            'device': 'desktop',
            'related': 'true',
            'st': 'product',
            'safe_search': 'false',

        }

        payload = generate_payload('SearchProductQuery', '_grab_category', {
                'params': urlencode(params)
            })

        print('{} page {}'.format(categ.name, page))
        return payload

    def parse_req(self, hasil) -> List[ProductItem]:
        for data in hasil['data']['CategoryProducts']['data']:
            productkey = data['url'].split('/')[-1]
            shopdomain = data['shop']['url'].split('/')[-1]

            shop = ShopItem(data['shop']['id'], data['shop']['name'], data['shop']['url'])
            product = ProductItem(
                data['id'],
                data['url'],
                shop,
                productkey,
                shopdomain
            )

            yield product



    def req(self, categ: Categ):
        payload = self.create_payload(categ)

        req = requests.post(_gql_uri, data=json.dumps(payload), headers = DEFAULT_HEADER)

        if req.status_code != 200:
            raise ApiExcetion(req.text)

        raw = json.loads(req.text)

        return self.parse_req(raw)

    def run(self):
        limitpage = 50
        
        for _ in range(0, limitpage):
            for categ in self.categories:
                categ: Categ = categ
                for pitem in self.req(categ):
                    yield pitem

                categ.last_page += 1


            self.save_obj()




if __name__ == '__main__':
    from pprint import pprint

    discover = DiscoverProduct()
    hasil = discover.run()
    for data in hasil:
        print(data.__dict__)
        print('\n\n')
    
            



