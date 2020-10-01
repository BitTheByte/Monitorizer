from collections import namedtuple
import threading
import types
import time


class Channel(object):
    def __init__(self, name='default'):
        self.name = name
        self.stop = False
        self.items = []
        self.jobs = 0
        self.__lock = threading.Lock()

    def append(self, *items):
        with self.__lock: self.jobs += 1
        self.items.append(items)

    def pop(self):
        try:
            return True, self.items.pop(0)
        except IndexError:
            return False, None

    def open(self):
        return not self.stop

    def wait(self):
        while self.jobs > 0:
            time.sleep(0.25)

    def close(self):
        self.stop = True


result = namedtuple("Result", "func ret args channel wid")


def _worker(wid, target, channel, lock, callback=None):
    while channel.open():
        ok, args = channel.pop()
        if not ok: time.sleep(0.50); continue
        retval = target(*args)
        with lock:
            channel.jobs -= 1

        if type(callback) != types.FunctionType and type(callback) != types.MethodType: continue

        callback(
            result(wid=wid, channel=channel, func=target, args=args, ret=retval)
        )


def workers(target, channel, count=5, callback=None):
    lock = threading.Lock()
    for _id in range(1, count + 1):
        threading.Thread(target=_worker, args=(_id, target, channel, lock, callback,)).start()
