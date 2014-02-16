# coding=utf-8
from __future__ import absolute_import
from django.shortcuts import render, redirect
from alyticsproc.tasks import get_testdata, exec_function, commit_results, complete_process
from .models import LastCheck
from celery import group


def index(request):
    lastcheck = LastCheck.get_instance()
    return render(request, 'index.html', {'lastcheck': lastcheck})


def start_processing(request):
    g = group(get_testdata.s(pk) | exec_function.s() | commit_results.s(pk)
              for pk in TestData.objects.filter(performed=False).values_list('pk', flat=True))
    (g | complete_process.s())()
    return redirect('index')