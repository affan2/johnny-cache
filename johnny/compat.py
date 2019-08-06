# coding: utf-8

"""
Tools to ease compatibility across supported versions of Django & Python.
"""


from django.db.models.sql import compiler

from queue import Queue

import django
from django.db import transaction

from django.utils.encoding import force_bytes, force_text
from django.utils.six import string_types, text_type


__all__ = (
    'Queue', 'force_bytes', 'force_text', 'string_types', 'text_type',
    'empty_iter', 'is_managed', 'managed',
)


def empty_iter():
    if django.VERSION[:2] >= (1, 5):
        return iter([])
    return compiler.empty_iter()


def is_managed(using=None):
    if django.VERSION[:2] < (1, 6):
        return transaction.is_managed(using=using)
    elif django.VERSION[:2] >= (1, 6):
        # See https://code.djangoproject.com/ticket/21004
        return not transaction.get_autocommit(using=using)
    return False


def managed(flag=True, using=None):
    if django.VERSION[:2] < (1, 6):
        transaction.managed(flag=flag, using=using)
    elif django.VERSION[:2] >= (1, 6):
        transaction.set_autocommit(not flag, using=using)
