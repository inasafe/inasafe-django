# coding=utf-8
import os
from celery.schedules import crontab
from kombu import Queue

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/16/16'


BROKER_URL = os.environ.get('BROKER_URL')
CELERY_RESULT_BACKEND = BROKER_URL

CELERY_ALWAYS_EAGER = False
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_IGNORE_RESULT = False
CELERY_SEND_EVENTS = True
CELERY_TASK_RESULT_EXPIRES = 24 * 3600
CELERY_DISABLE_RATE_LIMITS = True
CELERY_DEFAULT_QUEUE = "default"
CELERY_DEFAULT_EXCHANGE = "default"
CELERY_DEFAULT_EXCHANGE_TYPE = "direct"
CELERY_DEFAULT_ROUTING_KEY = "default"
CELERY_CREATE_MISSING_QUEUES = True

CELERY_QUEUES = [
    Queue('default', routing_key='default'),
    Queue('inasafe-realtime', routing_key='inasafe-realtime'),
    Queue('inasafe-django', routing_key='inasafe-django'),
]

CELERYBEAT_SCHEDULE = {
    # executes every hour
    'process-hourly-flood-report': {
        'task': 'realtime.tasks.flood.create_flood_report',
        'schedule': crontab(minute='0')
    },
    # executes every 2 minutes
    'check-realtime-broker-connection': {
        'task': 'realtime.tasks.indicator.check_realtime_broker',
        'schedule': crontab(minute='*/2')
    },
    # executes every night
    'send-indicator-status-nightly': {
        'task': 'realtime.tasks.indicator.notify_indicator_status',
        'schedule': crontab(hour='0', minute='0')
    },
    # executes every hour
    'retrieve-felt-earthquake-list': {
        'task': 'realtime.tasks.earthquake.retrieve_felt_earthquake_list',
        'schedule': crontab(minute='0')
    },
    # executes every minute
    'check-realtime-ash-processing': {
        'task': 'realtime.tasks.ash.check_processing_task',
        'schedule': crontab(minute='*')
    }
}

CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
