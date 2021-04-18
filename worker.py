from server import adapter, configuration
import tornado.ioloop

io_loop = tornado.ioloop.IOLoop.current()

adapter.receive(queue=configuration["publish"]["outgoing_1"]["exchange"])
adapter.receive(queue=configuration["publish"]["outgoing_2"]["exchange"])


io_loop.start()