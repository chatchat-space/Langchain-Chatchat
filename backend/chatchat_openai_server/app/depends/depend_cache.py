from app.depends.cache.base_cache import BaseCache

cache: BaseCache


def init_cache(config):
    global cache
    cache_type = config.get('cache_type', 'local_cache')
    if cache_type == 'local_cache':
        from app.depends.cache.local_cache import LocalCache
        cache = LocalCache(config)
    elif cache_type == 'redis_cache':
        from app.depends.cache.redis_cache import RedisCache
        cache = RedisCache(config)
