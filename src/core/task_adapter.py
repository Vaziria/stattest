import traceback
import dill
from typing import TypedDict, Callable

from tornado import gen

from .tasker import Tasker, ReqPayload

class TaskAdapter:
    
    func_list: dict

    def __init__(self):
        self.func_list = {}

    def serialize(self, body):
        return dill.dumps(body)

    def deserialize(self, body):
        return dill.loads(body)

    def task_response(self, req: ReqPayload):
        pass

    def get_handler(self, req: ReqPayload):
        funcname = req['funcname']
        return self.func_list.get(funcname)

    def register(self, receive_queue, publish_exchange):
        def decorate(func)-> Tasker:
            name = func.__name__
            if self.func_list.get(name, None):
                raise Exception('fungsi sudah diregist')
            
            task: Tasker = Tasker(name, func, self.emitter, receive_queue, publish_exchange)

            self.func_list[name] = func
            return task

        return decorate
    
    @gen.coroutine
    def emitter(self, req: ReqPayload, *arg, **karg):
        return True