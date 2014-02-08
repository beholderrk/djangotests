# coding=utf-8
from __future__ import absolute_import
from django.shortcuts import render, redirect
from alyticsproc.tasks import get_testdata, exec_function, commit_results, complete_process
from core.decorators import ajax_request
from .models import TestData, LastCheck
from celery import group


def index(request):
    lastcheck = LastCheck.get_instance()
    lastresults = TestData.objects.filter(performed=True).order_by('-date_modified')[:10]
    return render(request, 'index.html', {'lastcheck': lastcheck, 'lastresults': lastresults})


@ajax_request
def save_testdata(request):
    json_data = request.POST.get('json')
    TestData.objects.create(json_data=json_data)
    return {'success': True}


def start_processing(request):
    g = group(get_testdata.s(pk) | exec_function.s() | commit_results.s(pk)
              for pk in TestData.objects.filter(performed=False).values_list('pk', flat=True))
    (g | complete_process.s())()
    return redirect('index')