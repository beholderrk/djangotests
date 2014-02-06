# coding=utf-8
from __future__ import absolute_import
from django.shortcuts import render, redirect
from alyticsproc.tasks import get_testdata, exec_function, commit_results, complete_process
from core.decorators import ajax_request
from .models import TestData
from celery import group


@ajax_request
def index(request):
    if request.method == 'POST':
        json_data = request.POST.get('json')
        TestData.objects.create(json_data=json_data)
        return {'success': True}
    return render(request, 'index.html')


def start_processing(request):
    g = group(get_testdata.s(pk) | exec_function.s() | commit_results.s(pk)
              for pk in TestData.objects.filter(performed=False).values_list('pk', flat=True))
    (g | complete_process.s())()
    return redirect('index')