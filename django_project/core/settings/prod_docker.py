# noinspection PyUnresolvedReferences
from __future__ import unicode_literals
import os

from .prod import *  # noqa
from .celery_config import *  # noqa

ALLOWED_HOSTS = ['*']

ADMINS = (
    ('Tim Sutton', 'tim@kartoza.com'),
    ('Ismail Sunni', 'ismail@kartoza.com'),
    ('Christian Christellis', 'christian@kartoza.com'),
    ('Rizky Maulana Nugraha', 'rizky@kartoza.com'),
    # RM: will be left as it is as a tribute to Akbar :)
    # ('Akbar Gumbira', 'akbargumbira@gmail.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USERNAME'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
        'HOST': os.environ['DATABASE_HOST'],
        'PORT': 5432,
        'TEST': {
            'NAME': 'unittests',
        }
    }
}

MEDIA_ROOT = '/home/web/media'
STATIC_ROOT = '/home/web/static'

# See fig.yml file for postfix container definition
#
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# Host for sending e-mail.
EMAIL_HOST = 'smtp'
# Port for sending e-mail.
EMAIL_PORT = 25
# SMTP authentication information for EMAIL_HOST.
# See fig.yml for where these are defined
EMAIL_HOST_USER = 'noreply@kartoza.com'
EMAIL_HOST_PASSWORD = 'docker'
EMAIL_USE_TLS = False
EMAIL_SUBJECT_PREFIX = '[InaSAFE]'
DEFAULT_FROM_EMAIL = 'noreply@inasafe.org'


SITE_DOMAIN_NAME = unicode(os.environ.get(
    'SITE_DOMAIN_NAME', 'http://realtime.inasafe.org'))
