from pymongo import MongoClient

_client = MongoClient('localhost:9700')
_db = _client.tokpedstat