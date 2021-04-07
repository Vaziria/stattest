from typing import List
from pymongo import MongoClient

client = MongoClient('localhost:9700')
db = client.tokpedstat


def execute(data: List[dict]):
    collection = 'product'
    sort = {'created': -1 }
    

    datas = db[collection].find(*data).sort(sort).skip(1000).limit(10)

