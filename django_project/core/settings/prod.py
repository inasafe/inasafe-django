# -*- coding: utf-8 -*-
import os
import ast

from .project import *  # noqa

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'inasafe_dev',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        # Set to empty string for default.
        'PORT': '',
    }
}

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

if LOGGING_MAIL_ADMINS:
    mail_admins_handler = 'mail_admins'
else:
    mail_admins_handler = LOGGING_DEFAULT_HANDLER

if LOGGING_SENTRY:
    sentry_handler = 'sentry'
else:
    sentry_handler = LOGGING_DEFAULT_HANDLER

if 'raven.contrib.django.raven_compat' in INSTALLED_APPS:
    print '*********** Setting up sentry logging ************'
    RAVEN_CONFIG = {
        'dsn': 'http://05ac39e9c6754f71b697d0b694bca657'
               ':6c2a47fc6ce04ed2bb966df9454df7d3@sentry.kartoza.com/13',
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
        'disable_existing_loggers': True,
        # default root logger - handle with sentry
        'root': {
            'level': 'ERROR',
            'handlers': [sentry_handler],
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
                'propagate': False
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
