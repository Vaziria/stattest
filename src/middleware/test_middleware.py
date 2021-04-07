from .base import Middleware

class TestMiddleware(Middleware):
    def execute(self, context, nextcall):
        print('test middle')
        nextcall()


