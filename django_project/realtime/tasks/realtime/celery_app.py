# coding=utf-8

from celery import Celery

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/16/16'


app = Celery('realtime.tasks')
app.config_from_object('realtime.tasks.realtime.celeryconfig')
