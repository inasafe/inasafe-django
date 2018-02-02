# coding=utf-8
"""Sample file configuration for celery_app worker

This file is intended only for a sample.
Please copy it as celeryconfig.py so it can be read
"""

import os

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '1/28/16'


broker_url = os.environ.get('INASAFE_REALTIME_broker_url')

result_backend = broker_url

task_routes = {
    'realtime.tasks.flood': {
        'queue': 'inasafe-realtime'
    }
}
