# -*- coding: utf-8 -*-
from .contrib import *  # noqa

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        # Or path to database file if using sqlite3.
        'NAME': '',
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        # Empty for localhost through domain sockets or '127.0.0.1' for
        # localhost through TCP.
        'HOST': '',
        # Set to empty string for default.
        'PORT': '',
    }
}

# Project apps
INSTALLED_APPS += (
    'frontend',
    'realtime'
)


PIPELINE_JS = {
    'contrib': {
        'source_filenames': (
            'js/jquery-1.11.1.min.js',
            'js/bootstrap.js'
        ),
        'output_filename': 'js/contrib.js',
    },
    'appjs': {
        'source_filenames': (
            'js/csrf-ajax.js',
        ),
        'output_filename': 'js/appjs.js'
    },
    'dynatablejs': {
        'source_filenames': (
            'js/jquery.dynatable.js',
        ),
        'output_filename': 'js/jquery.dynatable.js'
    }
}

PIPELINE_CSS = {
    'contrib': {
        'source_filenames': (
            'css/bootstrap.min.css',
        ),
        'output_filename': 'css/contrib.css',
        'extra_context': {
            'media': 'screen, projection',
        },
    },
    'main': {
        'source_filenames': (
            'css/main.css',
        ),
        'output_filename': 'css/main.css',
        'extra_context': {
            'media': 'screen, projection',
        },
    },
    'dynatablejs': {
        'source_filenames': (
            'css/jquery.dynatable.css',
        ),
        'output_filename': 'css/jquery.dynatable.css',
        'extra_context': {
            'media': 'screen, projection',
        },
    }
}
