# import gc
import traceback
from queue import Queue
# from threading import Thread
# import threading
from typing import Optional, List, Dict, Any, TypeVar, Deque
from collections import deque
import torch
import transformers

from models.extensions.thread_with_exception import ThreadWithException
import models.shared as shared


K = TypeVar('K')
V = TypeVar('V')

class LimitedLengthDict(Dict[K, V]):
    def __init__(self, maxlen=None, *args, **kwargs):
        self.maxlen = maxlen
        self._keys: Deque[K] = deque()
        super().__init__(*args, **kwargs)

    def __setitem__(self, key: K, value: V):
        if key not in self:
            if self.maxlen is not None and len(self) >= self.maxlen:
                oldest_key = self._keys.popleft()
                if oldest_key in self:
                    del self[oldest_key]
        self._keys.append(key)
        super().__setitem__(key, value)


class FixedLengthQueue:
    # 停止符号列表
    stop_sequence: Optional[str] = []
    # 缓冲区
    max_length: int = 0
    # 缓冲区容器
    queue: deque = None
    # 输入区容器
    queue_in: LimitedLengthDict[int, str] = {}
    # 输出区容器
    queue_out: Dict[int, str] = {}

    def __new__(cls, *args, **kwargs):
        # 创建新的实例
        instance = super().__new__(cls)
        # 在这里可以对实例进行额外的设置
        return instance

    def __init__(self, stop_sequence):
        if stop_sequence is None:
            self.stop_sequence = []
            self.max_length = 0
        elif isinstance(stop_sequence, str):
            self.stop_sequence = [stop_sequence]
            self.max_length = 1
        else:
            self.stop_sequence = stop_sequence
            self.max_length = len(''.join(stop_sequence))

        self.queue = deque(maxlen=self.max_length)
        self.queue.clear()
        self.queue_in.clear()
        self.queue_out.clear()

    def add(self, index, item):
        self.queue_in[index] = item

    def _add_out(self, index, item):
        self.queue_out[index] = item

    def put_replace_out(self, index):
        return self.queue_out[index]

    def contains_replace_sequence(self):
        """
        替换字符
        :return:
        """

        for key, value in self.queue_in.items():

            word_index = value.rfind("：")
            if word_index != -1:
                value = value.replace("：", ":")

            word_index = value.rfind("[")
            if word_index != -1:
                value = value.replace("[", "")

            word_index = value.rfind("]")
            if word_index != -1:
                value = value.replace("]", "")

            self._add_out(key, value)

    def contains_stop_sequence(self):
        # 截取固定大小的数据判断
        self.queue.clear()
        last_three_keys = list(self.queue_out.keys())[-self.max_length:]
        joined_queue = ''.join([self.queue_out[key] for key in last_three_keys])
        for char in joined_queue:
            self.queue.append(char)

        joined_queue = ''.join(self.queue)
        # Initialize a variable to store the index of the last found stop string
        last_stop_str_index = -1

        # Iterate through the stop string list
        for stop_word in self.stop_sequence:
            # Find the last occurrence of the stop string in the output
            stop_word_index = joined_queue.rfind(stop_word)

            # If the stop string is found, compare the index with the previously found index
            if stop_word_index != -1 and stop_word_index > last_stop_str_index:
                last_stop_str_index = stop_word_index

        # Handle the last found stop string index here
        return last_stop_str_index

    def __repr__(self):
        return str(self.queue)


# Copied from https://github.com/PygmalionAI/gradio-ui/
class _SentinelTokenStoppingCriteria(transformers.StoppingCriteria):

    def __init__(self, sentinel_token_ids: list, starting_idx: int):
        transformers.StoppingCriteria.__init__(self)
        self.sentinel_token_ids = sentinel_token_ids
        self.starting_idx = starting_idx

    def __call__(self, input_ids: torch.LongTensor, _scores: torch.FloatTensor) -> bool:
        for sample in input_ids:
            trimmed_sample = sample[self.starting_idx:]

            for i in range(len(self.sentinel_token_ids)):
                # Can't unfold, output is still too tiny. Skip.
                if trimmed_sample.shape[-1] < self.sentinel_token_ids[i].shape[-1]:
                    continue
                for window in trimmed_sample.unfold(0, self.sentinel_token_ids[i].shape[-1], 1):
                    if torch.all(torch.eq(self.sentinel_token_ids[i][0], window)):
                        return True
        return False


class Stream(transformers.StoppingCriteria):
    def __init__(self, callback_func=None):
        self.callback_func = callback_func

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        if shared.stop_everything:
            raise ValueError
        if self.callback_func is not None:
            self.callback_func(input_ids[0])
        return False


class Iteratorize:
    """
    Transforms a function that takes a callback
    into a lazy iterator (generator).
    """

    thread: ThreadWithException = None

    def __new__(cls, *args, **kwargs):
        # 创建新的实例
        instance = super().__new__(cls)
        # 在这里可以对实例进行额外的设置
        return instance

    def __init__(self, func, kwargs={}, callback=None):
        self.mfunc = func
        self.c_callback = callback
        self.q = Queue()
        self.sentinel = object()
        self.kwargs = kwargs

        def _callback(val):
            if shared.stop_everything:
                raise ValueError
            self.q.put(val)

        def gen():
            try:
                ret = self.mfunc(callback=_callback, **self.kwargs)
            except ValueError:
                print("print(ValueError)")
            except:
                traceback.print_exc()
                print("traceback.print_exc()")
            self.q.put(self.sentinel)

        self.thread = ThreadWithException(target=gen)
        self.thread.start()

    def __iter__(self):
        shared.stop_everything = False
        return self

    def __next__(self):
        obj = self.q.get(True, None)
        if obj is self.sentinel:
            raise StopIteration
        else:
            return obj

    def __del__(self):
        shared.stop_everything = False
        self.q.empty()
        shared.loaderCheckPoint.clear_torch_cache()

    def __enter__(self):
        shared.stop_everything = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shared.stop_everything = True
        shared.loaderCheckPoint.clear_torch_cache()
        self.thread.raise_exception()
