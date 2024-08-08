from persistqueue import Queue

from app.extensions.mq.base_mq import BaseMqService


class LocalMqService(BaseMqService):
    def __init__(self, config):
        super().__init__(config)
        self.queue = Queue(config.get('path', './queue'))

    def enqueue(self, item):
        self.queue.put(item)

    def dequeue(self):
        return self.queue.get()

    def size(self):
        return self.queue.qsize()

    def is_empty(self):
        return self.queue.empty()
