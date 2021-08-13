from abc import ABCMeta, abstractmethod
import pymongo
import os
from datetime import datetime, timedelta

from vazutils.logger import Logger

logger = Logger(__name__)

MONGO_URI = os.environ.get('MONGO_URI', None)

logger.info(MONGO_URI)

client = pymongo.MongoClient(MONGO_URI)
db = client.tokpedstat



class DatabaseAdapt(metaclass=ABCMeta):
    @abstractmethod
    def upsert(self, data) -> bool:
        raise NotImplementedError


class MongoRepo(DatabaseAdapt):
    col = None

    def __init__(self):
        super().__init__()
        self.col = db[self.collection]

    @property
    @abstractmethod
    def collection(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def field_id(self):
        raise NotImplementedError

    def upsert(self, data):
        query =  {
            '_id': data[self.field_id]
        }

        cek = self.col.replace_one(query, data, upsert=True)

        return bool(cek)

    def upsert_created(self, data):
        query =  {
            '_id': data[self.field_id]
        }
        cek = self.col.find_one(query, {'_id': 1 })
        if cek:
            self.col.replace_one(query, data)
            return True

        data['created'] = datetime.now()
        self.col.replace_one(query, data, upsert = True)
        return True
    
    def delete(self, idnya):
        return self.col.delete_one({ '_id': idnya })


class ProductRepo(MongoRepo):
    collection = 'product'
    field_id = 'itemid'

    def get_not_updated(self, days, limit = 300000):

        limitday = datetime.utcnow() - timedelta(days = days)
        query = {
            'last_updated': {
                '$lte': limitday
            }
        }

        for data in self.col.find(query).limit(limit):
            yield data
        

class TokoRepo(MongoRepo):
    collection = 'toko'
    field_id = 'shopid'
    
    @classmethod
    def data_for_product(cls, idnya):
        projection = { 
            "username": 1,
             "location": 1,
            "kecepatan": 1, 
            "score_map": 1, 
            "rating": 1, 
            "percent_tx": 1,
        }
        
        return db[cls.collection].find_one({'_id': idnya}, projection)



    
    
    



if __name__ == '__main__':
    prod = ProductRepo()