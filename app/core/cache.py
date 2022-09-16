from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.core.cache import caches


class CacheMixin:
    """
    Mixing to cache regular page response
    """
    def __init__(self, cache_timeout=300):
        self.cache_timeout = cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.self.cache_timeout)(
            super(CacheMixin, self).dispatch)(*args, **kwargs)


class CacheHeaderMixin:
    """
    Mixing to cache private page response
    """
    def __init__(self, cache_timeout=300):
        self.cache_timeout = cache_timeout

    def dispatch(self, *args, **kwargs):
        return vary_on_headers('Authorization')(
                cache_page(self.cache_timeout)(
                        super(CacheHeaderMixin, self).dispatch))(
                            *args, **kwargs)

class Cache:
    """
    Caching individual keys
    """
    def __init__(self, key):
        self.cache = caches['default']
        self.key = key

    def get(self):
        return self.cache.get(self.key)

    def set(self, value, timeout=300):
        self.cache.set(self.key, value, timeout)

    def clear_cache(self):
        self.cache.delete_many(keys=self.cache.keys(self.key))
