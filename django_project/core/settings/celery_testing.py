# coding=utf-8

from .dev_docker import *  # noqa

# Redefine databases entry for unittests


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'unittests',
        'USER': 'docker',
        'PASSWORD': 'docker',
        'HOST': 'db',
        'PORT': 5432,
        'TEST': {
            'NAME': 'unittests',
        }
    }
}
