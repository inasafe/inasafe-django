# coding=utf-8

from celery import Celery
from django.conf import settings

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/16/16'


app = Celery('inasafe-django')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
