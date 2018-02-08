# coding=utf-8
import os
from celery.schedules import crontab
from kombu import Queue

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/16/16'


broker_url = os.environ.get('BROKER_URL')
result_backend = broker_url

task_always_eager = False
task_eager_propagates = True
task_ignore_result = False
worker_send_task_events = True
result_expires = 24 * 3600
worker_disable_rate_limits = True
task_default_queue = "default"
task_default_exchange = "default"
task_default_exchange_type = "direct"
task_default_routing_key = "default"
task_create_missing_queues = True
worker_concurrency = 1
worker_prefetch_multiplier = 1

task_queues = [
    Queue('default', routing_key='default'),
    Queue('inasafe-realtime', routing_key='inasafe-realtime'),
    Queue('inasafe-django', routing_key='inasafe-django'),
    Queue('inasafe-django-indicator', routing_key='inasafe-django-indicator'),
]

beat_schedule = {
    # executes every hour
    'process-hourly-flood-report': {
        'task': 'realtime.tasks.flood.create_flood_report',
        'schedule': crontab(minute='0'),
        'options': {
            'queue': 'inasafe-django'
        }
    },
    # executes every 2 minutes
    'check-realtime-broker-connection': {
        'task': 'realtime.tasks.indicator.check_realtime_broker',
        'schedule': crontab(minute='*/2'),
        'options': {
            'queue': 'inasafe-django-indicator'
        }
    },
    # executes every night
    'send-indicator-status-nightly': {
        'task': 'realtime.tasks.indicator.notify_indicator_status',
        # 'schedule': crontab(hour='0', minute='0'),
        'schedule': crontab(hour='0', minute='0'),
        'options': {
            'queue': 'inasafe-django-indicator'
        }
    },
    # executes every hour
    'retrieve-felt-earthquake-list': {
        'task': 'realtime.tasks.earthquake.retrieve_felt_earthquake_list',
        'schedule': crontab(minute='0'),
        'options': {
            'queue': 'inasafe-django'
        }
    },
    # executes every minute
    'check-realtime-ash-processing': {
        'task': 'realtime.tasks.ash.check_processing_task',
        'schedule': crontab(minute='*'),
        'options': {
            'queue': 'inasafe-django'
        }
    }
}

beat_scheduler = 'celery.beat.PersistentScheduler'
