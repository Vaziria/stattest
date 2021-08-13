from typing import List
from datetime import datetime
import requests
import json

from tokopedia_client.graphql.payload import generate_payload, _gql_uri

from ..models.product import Product
from ..error.api_error import ApiExcetion


# default header
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

class ProductItem:
    pass


def req_product_info(shopdomain, productkey):
    
    return generate_payload('PDPInfoQuery', '_grab_product', {
        "shopDomain": shopdomain,
        "productKey": productkey
    })

def get_product_info(shopdomain, productkey):

    payload = req_product_info(shopdomain, productkey)

    req = requests.post(_gql_uri, data=json.dumps(payload), headers = DEFAULT_HEADER)

    if req.status_code != 200:
        raise ApiExcetion(req.text)

    return json.loads(req.text)['data']['getPDPInfo']


def parse_product(rawprod) -> Product:

    categ = list(map(lambda x: x['id'], rawprod['category']['detail']))

    product = Product(
        rawprod['basic']['id'],
        rawprod['basic']['name'],
        rawprod['basic']['price'],
        rawprod['basic']['shopID'],
        rawprod['basic']['url'],
        rawprod['basic']['weight'],
        datetime.utcnow(),
        list(map(lambda x: x['url300'], rawprod['pictures'])),
        categ[0],
        categ[1],
        categ[2],
        rawprod['stock']['value'],
        rawprod['stats']['countView'],
        rawprod['stats']['countTalk'],
        rawprod['stats']['countReview'],
        0,
        0,
        rawprod['txStats']['itemSold'],
        rawprod['txStats']['txSuccess'],
        rawprod['basic']['description']

    )

    # product['description'] = rawprod['basic']['description']

    return product

class ProductChuck:
    urls: str = []

    def __init__(self, urls):
        self.urls = urls

    def get(self) -> List[Product]:
        payload = list(self.generate_payloads())
        headers = {
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

        req = requests.post(_gql_uri, data=json.dumps(payload), headers = headers)
        raw = json.loads(req.text)
        for data in raw:
            data = data['data']['getPDPInfo']
            yield parse_product(data)

    
    def generate_payloads(self):

        for url in self.urls:
            url = url.split('/')
            name = url[-1]
            shopname = url[-2]
            # payload = generate_payload('ProductShowcaseQuery', '_stat_query',
            # {
            #     "productID": 0,
            #     "productKey": name,
            #     "shopDomain": shopname

            # })

            payload = generate_payload('PDPInfoQuery', '_grab_product', {
                "shopDomain": shopname,
                "productKey": name
            })


            yield payload

    

if __name__ == '__main__':
    from pprint import pprint

    # urls = [
    #     'https://www.tokopedia.com/leluto/gitar-akustik-yamaha-apx-500ii-termurah?src=topads',
    #     'https://www.tokopedia.com/leluto/stand-gitar-bass-ukulele-elektrik-dudukan-gitar-penyangga-gitar-094-32'
    # ]
    # data = ProductChuck(urls)
    # print(data.get())

    raw = get_product_info('leluto', 'gitar-akustik-yamaha-apx-500ii-termurah')

    hasil = parse_product(raw)
    pprint(hasil.__dict__)