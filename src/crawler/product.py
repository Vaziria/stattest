from tokopedia_client.graphql.payload import generate_payload, _gql_uri
import requests
import json


# data model product not implemented

class ProductChuck:
    urls: str = []

    def __init__(self, urls):
        self.urls = urls

    def get(self):
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

        return req.text

    def generate_payloads(self):

        for url in self.urls:
            url = url.split('/')
            name = url[-1]
            shopname = url[-2]
            payload = generate_payload('ProductShowcaseQuery', '_stat_query',
            {
                "productID": 0,
                "productKey": name,
                "shopDomain": shopname

            })
            yield payload

if __name__ == '__main__':
    urls = [
        'https://www.tokopedia.com/leluto/gitar-akustik-yamaha-apx-500ii-termurah?src=topads',
        'https://www.tokopedia.com/leluto/stand-gitar-bass-ukulele-elektrik-dudukan-gitar-penyangga-gitar-094-32'
    ]
    data = ProductChuck(urls)
    print(data.get())