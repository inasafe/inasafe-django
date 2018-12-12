from .project import *  # noqa

# Set debug to True for development
DEBUG = True
TEMPLATE_DEBUG = DEBUG
LOGGING_OUTPUT_ENABLED = DEBUG
LOGGING_LOG_SQL = DEBUG
DEV_MODE = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable caching while in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        # define output formats
        'verbose': {
            'format': (
                '%(levelname)s %(name)s %(asctime)s %(module)s %(process)d '
                '%(thread)d %(message)s')
        },
        'simple': {
            'format': (
                '%(name)s %(levelname)s %(filename)s L%(lineno)s: '
                '%(message)s')
        },
    },
    'handlers': {
        # console output
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
        },
        # 'logfile': {
        #     'class': 'logging.FileHandler',
        #     'filename': '/tmp/app-dev.log',
        #     'formatter': 'simple',
        #     'level': 'DEBUG',
        # }
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',  # switch to DEBUG to show actual SQL
        },
        # example app logger
        # 'app.module': {
        #     'level': 'INFO',
        #     'handlers': ['logfile'],
        #     # propagate is True by default, which proppagates logs upstream
        #     'propagate': False
        # }
    },
    # root logger
    # non handled logs will propagate to the root logger
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG'
    }
}
