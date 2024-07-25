import asyncio
import threading
import uuid
from functools import lru_cache

from chatchat.server.core.lock.delay_queue import DelayQueue


@lru_cache(maxsize=1)
def get_default_delay_queue():
    return DelayQueue()


class DistributedLock:
    # lock的key
    lock_key = None
    #  锁超时时间
    lock_timout: float
    #  锁的过期时间，单位为秒
    lock_expire: float
    # 续期偏移量
    lock_offset = float
    #  延时队列(用于给锁续期)
    delay_queue: DelayQueue
    #  小于等于0时表示未加锁,大于0加锁
    state = 0
    owner: str

    def __init__(self, lock_key=None, lock_expire=60, lock_offset=4, delay_queue=None):
        self.lock_key = lock_key or str(uuid.uuid4())
        self.lock_expire = lock_expire
        self.lock_offset = lock_offset
        self.delay_queue = delay_queue or get_default_delay_queue()

    @property
    def is_locked(self):
        return self.state > 0

    def lock(self):
        ...

    def release(self):
        ...

    def renew_lock(self):
        ...

    def __enter__(self):
        return self.lock()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


# Example usage
if __name__ == "__main__":
    delay_queue = get_default_delay_queue()
    delay_queue.start()

    lock = DistributedLock.create('aaa')
    print(lock.lock())
    print(lock.release())
