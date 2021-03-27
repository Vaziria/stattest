import os
import pickle
from datetime import datetime, timedelta
import hashlib

class Context:
    hash_query = None
    query = None
    data = None
    def __init__(self, query):
        hash = hashlib.md5()
        hash.update(pickle.dumps(query))

        self.hash_query = hash.hexdigest()
        self.query = query

class CacheData:
    expires_in = None
    data = None

    def __init__(self, expires, data):
        self.expires_in = expires
        self.data = data


class Cache:
    dir = 'cache'
    expireMin = 1
    def __init__(self):
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

    def gen_expire(self):
        return datetime.now() + timedelta(min=1)
    
    def __call__(self, context: Context):
        data = self.get(context.hash_query)
        if not data:
            return False

        selisih = datetime.now() - data.expires_in
        if (selisih/60) > self.expireMin:

            return False
        return data
        

    def get(self, key)->CacheData:
        fname = '{}/{}.pkl'.format(self.dir, key)
        if not os.path.exists(fname):
            return False

        with open(fname, 'rb') as out:
            return pickle.load(out)

    def save(self, key, data):
        fname = '{}/{}.pkl'.format(self.dir, key)

        payload = CacheData(self.gen_expire(), data)
        
        with open(fname, 'w+b') as out:
            return pickle.dump(payload, out)
        

class Middleware:
    middle = []
    def __init__(self):
        self.middle = []

    def add_middle(self, middle):
        self.middle.append(middle)

    def __call__(self, context: Context):

        res = context
        for middle in self.middle:
            res = middle(res)

        return res 
            


if __name__ == '__main__':
    pass
