from .middleware.base import Handler
from .middleware.cache_middleware import CacheMiddleware, QueryContext
from .middleware.test_middleware import TestMiddleware

handler = Handler()
handler.add_middleware(CacheMiddleware())
handler.add_middleware(TestMiddleware())

if __name__ == '__main__':

    context = QueryContext('asdasdasdasd')

    handler(context)




