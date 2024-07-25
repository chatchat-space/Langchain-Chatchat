import asyncio
import threading
import uuid
from functools import lru_cache

from chatchat.server.core.lock.base import get_default_delay_queue, DistributedLock
from chatchat.server.core.lock.delay_queue import DelayQueue


class DefaultDistributedLock(DistributedLock):

    def __init__(self, lock_key=None, lock_expire=60, lock_offset=4, delay_queue=None):
        super().__init__(lock_key, lock_expire, lock_offset, delay_queue)

    @property
    def is_locked(self):
        return self.state > 0

    def lock(self):
        if self.is_locked:
            return False
        else:
            self.state = 1
            self.owner = threading.current_thread().name
            print(f"Lock acquired: {self.lock_key}")
            self.delay_queue.add_task(self.renew_lock, self.lock_expire - self.lock_offset)
        return self.is_locked

    def release(self):
        self.state = 0
        return not self.is_locked

    def renew_lock(self):
        # Simulate lock renewal
        print(f"Renewing lock: {self.lock_key}")
        if self.is_locked:
            self.delay_queue.add_task(self.renew_lock, self.lock_expire - self.lock_offset)

    def __enter__(self):
        return self.lock()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


# Example usage
if __name__ == "__main__":
    delay_queue = get_default_delay_queue()
    delay_queue.start()

    lock = DefaultDistributedLock('aa')
    print(lock.lock())
