from typing import List


class Context:
    pass

class Middleware:
    def execute(self, context: Context, nextcall):
        pass

class Handler:
    middleware = []
    def __init__(self):
        self.middleware = []

    def add_middleware(self, middleware: Middleware):
        self.middleware.append(middleware)

    def __call__(self, context):
        middles = iter(self.middleware)

        middle = next(middles)
        
        while isinstance(middle, Middleware):
            nextfunc = self.next(middles, context)
            middle = middle.execute(context, nextfunc)

        return middle

    def next(self, middle, context):

        def run():
            try:
                return next(middle)
            except StopIteration:
                return context

        return run



if __name__ == '__main__':
    handler = Handler()

    class Test(Middleware):
        def execute(self, middle, context):
            print('test middle')
            return next(middle)

    class Test2(Middleware):
        def execute(self, middle, context):
            print('test middle 2')

    handler.add_middleware(Test())
    handler.add_middleware(Test2())


    handler({})