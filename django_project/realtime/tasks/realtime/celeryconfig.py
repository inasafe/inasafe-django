# coding=utf-8
"""Sample file configuration for celery_app worker

This file is intended only for a sample.
Please copy it as celeryconfig.py so it can be read
"""

import os

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '1/28/16'


broker_url = os.environ.get('INASAFE_REALTIME_BROKER_URL')

result_backend = broker_url

task_serializer = 'pickle'
accept_content = {'pickle'}
result_serializer = 'pickle'


# Late ACK settings
task_acks_late = True
task_reject_on_worker_lost = True
