import dill
import uuid
from typing import TypedDict, Callable

from tornado import gen

class ReqPayload(TypedDict):
    funcname: str
    arg: list
    kwarg: dict

class Tasker:
    func: Callable
    name: str
    emitter: Callable
    receive_queue = ''
    publish_exchange = ''
    
    def __init__(self, name: str, func: Callable, emitter: Callable, receive_queue, publish_exchange):
        self.func = func
        self.name = name
        self.emitter = emitter
        self.receive_queue = receive_queue
        self.publish_exchange = publish_exchange

    def __call__(self, *arg, **kwarg):
        return self.func(*arg, **kwarg)

    def execute(self, *arg, **kwarg):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        req: ReqPayload = {
            'funcname': self.name,
            'arg': arg,
            'kwarg': kwarg
        }

        return self.emitter(req, receive_queue=self.receive_queue, publish_exchange=self.publish_exchange, timeout=200, ttl=200)
