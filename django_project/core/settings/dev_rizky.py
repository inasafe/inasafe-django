# -*- coding: utf-8 -*-
import sys
from .dev import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'gis',
        'USER': 'docker',
        'PASSWORD': 'docker',
        'HOST': 'localhost',
        'PORT': 6543
    }
}

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

if TESTING:
    MEDIA_ROOT = ABS_PATH('media_test')
