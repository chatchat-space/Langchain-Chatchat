# Python program raising
# exceptions in a python
# thread

import threading
import ctypes
import time


class ThreadWithException(threading.Thread):

    def get_id(self):
        return self.ident

    def raise_exception(self):
        """raises the exception, performs cleanup if needed"""
        try:
            thread_id = self.get_id()
            tid = ctypes.c_long(thread_id)
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(SystemExit))
            if res == 0:
                # pass
                raise ValueError("invalid thread id")
            elif res != 1:
                # """if it returns a number greater than one, you're in trouble,
                # and you should call it again with exc=NULL to revert the effect"""
                ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
                raise SystemError("PyThreadState_SetAsyncExc failed")
        except Exception as err:
            print(err)
