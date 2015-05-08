# -*- coding: utf-8 -*-
from .project import *  # noqa

# Set debug to True for testing
DEBUG = True
TEMPLATE_DEBUG = DEBUG
LOGGING_OUTPUT_ENABLED = DEBUG
LOGGING_LOG_SQL = DEBUG

# Use default Django test runner
TEST_RUNNER = 'django.test.runner.DiscoverRunner'


EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# change this to a proper location
EMAIL_FILE_PATH = '/tmp/'


# Do not log anything during testing
LOGGING = {
    # internal dictConfig version - DON'T CHANGE
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'nullhandler': {
            'class': 'logging.NullHandler',
        },
    },
    # default root logger
    'root': {
        'level': 'DEBUG',
        'handlers': ['nullhandler'],
    }
}
