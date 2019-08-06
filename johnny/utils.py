#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect

"""Extra johnny utilities."""

from .cache import get_backend, local, patch, unpatch
from .decorators import wraps, available_attrs


__all__ = ["celery_enable_all", "celery_task_wrapper", "johnny_task_wrapper", "utils_cache.py", ]


def prerun_handler(*args, **kwargs):
    """Celery pre-run handler.  Enables johnny-cache."""
    patch()


def postrun_handler(*args, **kwargs):
    """Celery postrun handler.  Unpatches and clears the localstore."""
    unpatch()
    local.clear()


def celery_enable_all():
    """Enable johnny-cache in all celery tasks, clearing the local-store
    after each task."""
    from celery.signals import task_prerun, task_postrun, task_failure
    task_prerun.connect(prerun_handler)
    task_postrun.connect(postrun_handler)
    # Also have to cleanup on failure.
    task_failure.connect(postrun_handler)


def celery_task_wrapper(f):
    """
    Provides a task wrapper for celery that sets up cache and ensures
    that the local store is cleared after completion
    """

    @wraps(f, assigned=available_attrs(f))
    def newf(*args, **kwargs):
        backend = get_backend()
        was_patched = backend._patched
        get_backend().patch()
        # since this function takes all keyword arguments,
        # we will pass only the ones the function below accepts,
        # just as celery does
        supported_keys = fun_takes_kwargs(f, kwargs)
        new_kwargs = dict((key, val) for key, val in list(kwargs.items())
                                if key in supported_keys)

        try:
            ret = f(*args, **new_kwargs)
        finally:
            local.clear()
        if not was_patched:
            get_backend().unpatch()
        return ret
    return newf


# Added by Mohammad Abouchama to replace functionality provided by celery.utils.fun_takes_kwargs.
# This is because the function fun_takes_kwargs is not available in celery 4.3.
# But it is still needed by some packages, such as johnny-cache.
# This is a copy of an old celery version used in the v2 of thebimhub.com.
# Adapted it for Python 3.6.
def fun_takes_kwargs(fun, kwlist):
    """With a function, and a list of keyword arguments, returns arguments in the list which the function takes."""
    S = getattr(fun, 'getfullargspec', inspect.getfullargspec(fun))
    # in getfullargspec varkw is instead of getargspec.keywords for ** parameters.
    if S.varkw is not None:
        return kwlist
    return [kw for kw in kwlist if kw in S.args]


# backwards compatible alias
johnny_task_wrapper = celery_task_wrapper

