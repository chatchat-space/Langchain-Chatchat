from abc import abstractmethod


class BaseCache:

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def get(self, key):
        raise NotImplementedError

    @abstractmethod
    def set(self, key, value):
        raise NotImplementedError

    @abstractmethod
    def delete(self, key):
        raise NotImplementedError
