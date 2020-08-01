# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import ast

from .project import *  # noqa

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# enable cached storage - requires uglify.js (node.js)
STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
MIDDLEWARE_CLASSES += (
    'django.middleware.gzip.GZipMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',
)

# define template function (example for underscore)
# PIPELINE_TEMPLATE_FUNC = '_.template'
PIPELINE_YUI_BINARY = '/usr/bin/yui-compressor'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
PIPELINE_YUI_JS_ARGUMENTS = '--nomunge'
PIPELINE_DISABLE_WRAPPER = True

# Comment if you are not running behind proxy
USE_X_FORWARDED_HOST = True

# Set debug to false for production
DEBUG = TEMPLATE_DEBUG = False

LOGGING_MAIL_ADMINS = ast.literal_eval(
    os.environ.get('LOGGING_MAIL_ADMINS', 'False'))
LOGGING_SENTRY = ast.literal_eval(
    os.environ.get('LOGGING_SENTRY', 'False'))

LOGGING_DEFAULT_HANDLER = os.environ.get('LOGGING_DEFAULT_HANDLER', 'console')
LOGGING_DEFAULT_LOG_LEVEL = os.environ.get(
    'LOGGING_DEFAULT_LOG_LEVEL', 'ERROR')

default_handlers = [LOGGING_DEFAULT_HANDLER]

if LOGGING_MAIL_ADMINS:
    mail_admins_handler = 'mail_admins'
else:
    mail_admins_handler = LOGGING_DEFAULT_HANDLER

if LOGGING_SENTRY:
    sentry_handler = 'sentry'
    default_handlers.append('sentry')
else:
    sentry_handler = LOGGING_DEFAULT_HANDLER

if 'raven.contrib.django.raven_compat' in INSTALLED_APPS:
    print('*********** Setting up sentry logging ************')
    RAVEN_CONFIG = {
        'dsn': 'http://8d4da28ebc7a4f848b864910ce31c250:'
               'aa93ab1e08024b93af023931148aeedb@sentry.kartoza.com/14',
    }

    # MIDDLEWARE_CLASSES = (
    #     'raven.contrib.django.middleware.SentryResponseErrorIdMiddleware',
    #     'raven.contrib.django.middleware.SentryLogMiddleware',
    # ) + MIDDLEWARE_CLASSES

    #
    # Sentry settings - logs exceptions to a database
    LOGGING = {
        # internal dictConfig version - DON'T CHANGE
        'version': 1,
        'disable_existing_loggers': False,
        # default root logger
        'root': {
            'level': LOGGING_DEFAULT_LOG_LEVEL,
            'handlers': default_handlers,
        },
        'handlers': {
            # send email to mail_admins, if DEBUG=False
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler'
            },
            # sentry logger
            'sentry': {
                'level': 'WARNING',
                'class': (
                    'raven.contrib.django.raven_compat.'
                    'handlers.SentryHandler'),
            },
            # file logger
            'logfile': {
                'class': 'logging.FileHandler',
                'filename': '/var/log/django.log',
                'level': 'DEBUG'
            },
            # console output
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
            },
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': [sentry_handler],
                'propagate': True
            },
            'raven': {
                'level': 'ERROR',
                'handlers': [mail_admins_handler],
                'propagate': False
            },
            'sentry.errors': {
                'level': 'ERROR',
                'handlers': [mail_admins_handler],
                'propagate': False
            },
            'django.request': {
                'handlers': [mail_admins_handler],
                'level': 'ERROR',
                'propagate': True
            }
        }
    }
