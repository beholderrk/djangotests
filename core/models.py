from django.db import models
from django.shortcuts import _get_queryset
from django.db.models.query import QuerySet


def get_first_or_None(qsinit, *args, **kwargs):
    if not qsinit:
        return None

    if isinstance(qsinit, list):
        try:
            return qsinit[0]
        except IndexError:
            return None

    if isinstance(qsinit, QuerySet):
        queryset = qsinit
    elif isinstance(qsinit, type):
        queryset = _get_queryset(qsinit)
    try:
        return queryset.filter(*args, **kwargs)[0]
    except IndexError:
        return None


class DateTimeModel(models.Model):
    date_modified = models.DateTimeField(auto_now=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True