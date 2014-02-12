# coding=utf-8
from __future__ import absolute_import
import re
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
        res = nii_function(json_str)
        if re.match(r'{"result": \d+}', res):
            return res
        else:
            raise Exception('nii_function result have wrong format')
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
    elif isinstance(res, str):
        data.result = res
    data.save()
    return not data.error


@app.task
def complete_process(results):
    """
    Задача выполняется после того как все наборы данных обработаны
    задача сохраняет общий результат последней обработки
    @param results: результаты последней обработки данных в виде [bool, bool] или bool
    """
    count = len(results) if isinstance(results, (list, tuple)) else 1
    all_true = all(results) if count > 1 else bool(results)
    if all_true:
        LastCheck.set_success(count)
    else:
        LastCheck.set_fail(count)