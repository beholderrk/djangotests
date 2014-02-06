# coding=utf-8
from __future__ import absolute_import
import collections
import json, itertools
from djangotests.celery import app
from alyticsproc.function import nii_function
from alyticsproc.models import TestData, LastCheck


@app.task
def get_testdata(pk):
    """
    берем тестовые данные из базы
    @param pk: pk модели TestData
    @return json набор данных
    """
    data = TestData.objects.get(pk=pk)
    return data.json_data


@app.task
def exec_function(json_str):
    """
    выполняем проверку nii_function на тестовых данных
    @param json_str: json набор данных вида [{},{},{}]
    @return либо результат выполнения либо объект exception
    """
    try:
        return nii_function(json_str)
    except Exception as ex:
        return ex


@app.task
def commit_results(res, pk):
    """
    сохраняем результат или ошибку обратно в бд
    @param res: результат выполнения, либо {} либо Exception
    @param pk: id записи в бд
    @return: результат проверки функции (bool)
    """
    data = TestData.objects.get(pk=pk)
    data.performed = True
    if isinstance(res, Exception):
        data.error = True
        data.exception = res.__unicode__()
    elif isinstance(res, dict):
        data.result = json.dumps(res)
    data.save()
    return not data.error


@app.task
def complete_process(results):
    count = len(results) if isinstance(results, (list, tuple)) else 1
    all_true = all(results) if count > 1 else bool(results)
    if all_true:
        LastCheck.set_success(count)
    else:
        LastCheck.set_fail(count)