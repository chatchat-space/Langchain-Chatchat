import persistqueue

from app.depends.mq.base_mq import BaseMqService


class LocalMqService(BaseMqService):
    def __init__(self, config):
        super().__init__(config)
        path = config.get('path', './queue')
        self.queue = persistqueue.SQLiteQueue(path, multithreading=True)

    def enqueue(self, item):
        self.queue.put(item)

    def dequeue(self):
        return self.queue.get()

    def size(self):
        return self.queue.qsize()

    def is_empty(self):
        return self.queue.empty()
