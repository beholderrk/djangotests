# coding=utf-8
from functools import wraps
from django.http import HttpResponse
import json


class JsonResponse(HttpResponse):
    """
    HttpResponse descendant, which return response with ``application/json`` mimetype.
    """
    def __init__(self, data):
        super(JsonResponse, self).__init__(content=json.dumps(data), mimetype='application/json')


def ajax_request(func):
    """ Декоратор для ajax запоросов """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if isinstance(response, dict) or isinstance(response, list):
            return JsonResponse(response)
        else:
            return response
    return wrapper
