import redis

from app.depends.cache.base_cache import BaseCache


class RedisCache(BaseCache):

    def __init__(self, config):
        super().__init__(config)
        self.client = redis.StrictRedis(
            host=config.get('host', 'localhost'),
            port=config.get('port', 6379),
            db=config.get('db', 0),
            password=config.get('password', None),
            decode_responses=True  # Automatically decode strings to Python str
        )

    def get(self, key):
        return self.client.get(key)

    def set(self, key, value):
        self.client.set(key, value)

    def delete(self, key):
        self.client.delete(key)
