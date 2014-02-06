from __future__ import absolute_import
from celery import Celery
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangotests.settings')

app = Celery('djangotests', backend='amqp', broker='amqp://guest@localhost//')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)