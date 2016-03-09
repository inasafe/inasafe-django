# coding=utf-8

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '1/28/16'


BROKER_URL = 'amqp://guest:guest@192.168.99.100:8100/'

CELERY_RESULT_BACKEND = BROKER_URL

CELERY_ROUTES = {
    'realtime.tasks.flood': {
        'queue': 'inasafe-realtime'
    }
}
