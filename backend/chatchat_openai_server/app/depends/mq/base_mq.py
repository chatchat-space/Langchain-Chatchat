from abc import ABC, abstractmethod


class BaseMqService(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def enqueue(self, item):
        """Add an item to the queue"""
        raise NotImplementedError

    @abstractmethod
    def dequeue(self):
        """Remove and return an item from the queue"""
        raise NotImplementedError

    @abstractmethod
    def size(self):
        """Return the size of the queue"""
        raise NotImplementedError

    @abstractmethod
    def is_empty(self):
        """Return whether the queue is empty"""
        raise NotImplementedError
