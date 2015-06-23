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
