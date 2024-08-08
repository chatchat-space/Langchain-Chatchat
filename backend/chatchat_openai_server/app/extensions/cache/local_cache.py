from diskcache import FanoutCache

from app.extensions.cache.base_cache import BaseCache


class LocalCache(BaseCache):

    def get(self, key, default=None):
        return self.cache.get(key, default=default)

    def set(self, key, value, expire=None):
        return self.cache.set(key, value, expire=expire)

    def delete(self, key):
        return self.cache.delete(key)

    def __init__(self, config):
        super().__init__(config)
        self.cache: FanoutCache = FanoutCache(**config)
