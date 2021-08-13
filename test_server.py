import asyncio
from tornado import web
from src.adapter import adapter, configuration, io_loop
from src import crawler_app
from tornado import gen
import json

class MainHandler(web.RequestHandler):
    @gen.coroutine
    def get(self):
        
        # res = yield crawler_app.get_info_toko.execute('diskonlaptop')
        res = yield crawler_app.test.execute()
        # self.write("{}".format(json.dumps(res.__dict__, default=str)))
        self.write("{}".format(json.dumps(res, default=str)))

def make_app():
    return web.Application([
        (r"/", MainHandler),
    ])


if __name__ == '__main__':
    app = make_app()
    app.rabbit_adapter = adapter
    app.listen(8888)
    print('running in 8888')
    io_loop.run_forever()