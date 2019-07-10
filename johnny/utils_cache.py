from django.core.cache import _create_cache
from django.core import signals


# Based on a solution provided by vstoykov in django-imagekit.
# https://github.com/vstoykov/django-imagekit/commit/c26f8a0
def get_cache(backend, **kwargs):
    """
    Compatibility wrapper for getting Django's cache backend instance
    """

    cache = _create_cache(backend, **kwargs)
    # Some caches -- python-memcached in particular -- need to do a cleanup at the
    # end of a request cycle. If not implemented in a particular backend
    # cache.close is a no-op
    signals.request_finished.connect(cache.close)
    return cache
