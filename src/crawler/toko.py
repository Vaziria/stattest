import requests
import json
from datetime import datetime

from tokopedia_client.graphql.payload import generate_payload, _gql_uri

from ..error.api_error import ApiExcetion
from ..models.toko import Toko

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

def req_toko(domain: str):
    payload = generate_payload('ShopInfoCore', '_shop_info_core', {
        "id": 0,
        "domain": domain
    })

    req = requests.post(_gql_uri, data=json.dumps(payload), headers = DEFAULT_HEADER)

    if req.status_code != 200:
        raise ApiExcetion(req.text)

    return json.loads(req.text)['data']['shopInfoByID']['result'][0]

def req_toko_stat(shopid: int):
    payload = generate_payload('ShopStatisticQuery', '_shop_statistic_Query', {
        "shopID": int(shopid)
    })

    req = requests.post(_gql_uri, data=json.dumps(payload), headers = DEFAULT_HEADER)

    if req.status_code != 200:
        raise ApiExcetion(req.text)

    return json.loads(req.text)['data']

def parse_toko(rawtoko, stat) -> Toko:
    percent_tx = float(int(rawtoko['shopStats']['totalTxSuccess']) / int(rawtoko['shopStats']['totalTx'])) * 100
    percent_tx = round(percent_tx, 3) 
    
    toko = Toko(
        int(rawtoko['shopCore']['shopID']),
        rawtoko['shopCore']['domain'],
        'https://tokopedia.com/{}'.format(rawtoko['shopCore']['domain']),
        rawtoko['shippingLoc']['cityName'],
        rawtoko['shippingLoc']['districtName'],
        int(rawtoko['activeProduct']),
        int(rawtoko['shopStats']['productSold']),
        int(rawtoko['shopStats']['totalTxSuccess']),
        percent_tx,
        rawtoko['location'],
        stat['shopRating']['ratingScore'],
        stat['shopRating']['totalReview'],
        int(stat['shopReputation'][0]['score_map']),
        int(stat['shopReputation'][0]['score'].replace('.', '')),
        int(stat['shopSatisfaction']['recentOneMonth']['bad']),
        int(stat['shopSatisfaction']['recentOneMonth']['good']),
        int(stat['shopSatisfaction']['recentOneMonth']['neutral']),
        datetime.utcnow()
    )
    

    return toko




if __name__ == '__main__':
    from pprint import pprint
    shop = req_toko('diskonlaptop')
    stat = req_toko_stat(shop['shopCore']['shopID'])
    print(stat)

    hasil = parse_toko(shop, stat)
    pprint(hasil.__dict__)