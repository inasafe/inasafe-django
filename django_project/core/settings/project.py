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


PIPELINE_TEMPLATE_SEPARATOR = '__'

PIPELINE_JS = {
    'contrib': {
        'source_filenames': (
            'js/jquery-1.11.1.min.js',
            'js/bootstrap.js',
        ),
        'output_filename': 'js/contrib.js',
    },
    'appjs': {
        'source_filenames': (
            'js/csrf-ajax.js',
        ),
        'output_filename': 'js/appjs.js'
    },
    'realtime_contrib': {
        'source_filenames': (
            'realtime/js/jquery.dynatable.js',
            'realtime/js/leaflet.markercluster-src.js',
            'realtime/js/locationfilter.js',
            'realtime/js/validator.js',
            'realtime/js/moment.js',
            'realtime/js/moment-timezone-all-years.js',
            'realtime/js/typeahead.jquery.js',
            'realtime/js/sprintf.js',
        ),
        'output_filename': 'js/realtime_contrib.js',
    },
    'realtime_appjs': {
        'source_filenames': (
            'realtime/js/realtime.js',
        ),
        'output_filename': 'js/realtime_appjs.js'
    },
    'realtime_shakejs': {
        'source_filenames': (
            'realtime/js/earthquake/shake.js',
            'realtime/js/templates/earthquake/*.jst'
        ),
        'output_filename': 'js/realtime_shakejs.js'
    },
    'realtime_floodjs': {
        'source_filenames': (
            'realtime/js/flood/flood.js',
            'realtime/js/templates/flood/*.jst'
        ),
        'output_filename': 'js/realtime_floodjs.js'
    },
    'realtime_ashjs': {
        'source_filenames': (
            'realtime/js/ash/ash.js',
            'realtime/js/templates/ash/*.jst'
        ),
        'output_filename': 'js/realtime_ashjs.js'
    },
    'usermap_contrib': {
        'source_filenames': (
            'user_map/js/leaflet.markercluster-src.js',
            'user_map/js/validate.js',
        ),
        'output_filename': 'js/usermap_contrib.js',
    },
    'usermap_appjs': {
        'source_filenames': (
            'user_map/js/user-map.js',
        ),
        'output_filename': 'js/usermap_appjs.js'
    },
}

PIPELINE_CSS = {
    'contrib': {
        'source_filenames': (
            'css/bootstrap.min.css',
            'css/inasafe-blog-style.css'
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
    'realtime_contrib': {
        'source_filenames': (
            'realtime/css/jquery.dynatable.css',
            'realtime/css/locationfilter.css',
            'realtime/css/MarkerCluster.css',
            'realtime/css/MarkerCluster.user-map.css'
        ),
        'output_filename': 'css/realtime_contrib.css',
        'extra_context': {
            'media': 'screen, projection',
        },
    },
    'realtime_appcss': {
        'source_filenames': (
            'realtime/css/realtime.css',
        ),
        'output_filename': 'css/realtime_appcss.css',
        'extra_context': {
            'media': 'screen, projection'
        }
    },
    'realtime_shakecss': {
        'source_filenames': (
            'realtime/css/earthquake/shake.css',
        ),
        'output_filename': 'css/realtime_shakecss.css',
        'extra_context': {
            'media': 'screen, projection'
        }
    },
    'realtime_floodcss': {
        'source_filenames': (
            'realtime/css/flood/flood.css',
        ),
        'output_filename': 'css/realtime_floodcss.css',
        'extra_context': {
            'media': 'screen, projection'
        }
    },
    'realtime_ashcss': {
        'source_filenames': (
            'realtime/css/ash/ash.css',
        ),
        'output_filename': 'css/realtime_ashcss.css',
        'extra_context': {
            'media': 'screen, projection'
        }
    },
    'usermap_contrib': {
        'source_filenames': (
            'user_map/css/MarkerCluster.css',
        ),
        'output_filename': 'css/usermap_contrib.css',
        'extra_context': {
            'media': 'screen, projection'
        }
    },
    'usermap_appcss': {
        'source_filenames': (
            'user_map/css/MarkerCluster.user-map.css',
            'user_map/css/user-map.css',
        ),
        'output_filename': 'css/usermap_appcss.css',
        'extra_context': {
            'media': 'screen, projection'
        }
    },
}
