# coding=utf-8
from __future__ import absolute_import
import json
import re
import sys
import traceback
from djangotests.celery import app
from alyticsproc.function import nii_function
from alyticsproc.models import LastCheck, DataItem, DataSet, ExecHistory


@app.task
def get_testdata(pk):
    """
    берем тестовые данные из базы
    @param pk: pk модели TestData
    @return json набор данных
    """
    data = DataSet.objects.get(pk=pk)
    items = [{'a': item.a, 'b': item.b} for item in data.dataitem_set.all()]
    return json.dumps(items)


@app.task
def exec_function(json_str):
    """
    выполняем проверку nii_function на тестовых данных
    @param json_str: json набор данных вида [{},{},{}]
    @return либо результат выполнения либо объект exception
    """
    try:
        res = nii_function(json_str)
        if re.match(r'\{\s*"result"\s*:\s*\d+\s*\}', res):
            return res
        else:
            raise Exception('nii_function result have wrong format')
    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        ex_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
        ex.message = ''.join(ex_list)
        return ex


@app.task
def commit_results(res, pk):
    """
    сохраняем результат или ошибку обратно в бд
    @param res: результат выполнения, либо {} либо Exception
    @param pk: id записи в бд
    @return: результат проверки функции (bool)
    """
    data = DataSet.objects.get(pk=pk)
    if isinstance(res, Exception):
        data.exechistory = ExecHistory(success=False, error=True, exception=res.message)
    else:
        data.exechistory = ExecHistory(success=True, error=False, result=res)
    data.exechistory.save()
    data.save()
    return data.exechistory.success


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