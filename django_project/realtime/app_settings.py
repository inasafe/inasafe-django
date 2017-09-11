# coding=utf-8
"""Configurations file for Realtime.

..note: By design, you can override these settings from your project's
    settings.py with prefix 'REALTIME' on the variable e.g
    'REALTIME_USER_ICONS'.

    For mailing. as the default, it wil use 'DEFAULT_FROM_MAIL' setting from
    the project.
"""
from datetime import timedelta
from django.conf import settings

LOGGER_NAME = 'InaSAFE Realtime REST Server'

# PROJECT_NAME: The project name for this apps e.g InaSAFE
default_project_name = 'InaSAFE Realtime'
PROJECT_NAME = getattr(settings, 'REALTIME_PROJECT_NAME',
                       default_project_name)

# LOGO/BRAND
default_brand_logo = 'realtime/img/logo.png'
BRAND_LOGO = getattr(settings, 'REALTIME_BRAND_LOGO', default_brand_logo)

# FAVICON_FILE: Favicon for this apps
default_favicon_file = 'realtime/img/inasafe-icon.png'
FAVICON_FILE = getattr(settings, 'REALTIME_FAVICON_FILE',
                       default_favicon_file)


# LEAFLET CONFIG
default_leaflet_tiles = (
    [
        'OpenStreetMap',
    ],
    [
        'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    ],
    [
        'abc',
    ],
    [
        '© <a href="http://www.openstreetmap.org" target="_parent">'
        'OpenStreetMap'
        '</a> and contributors, under an <a '
        'href="http://www.openstreetmap.org/copyright" target="_parent">'
        'open license</a>.',
    ]
)
LEAFLET_TILES = getattr(settings, 'LEAFLET_TILES', default_leaflet_tiles)

# Realtime Group:
default_realtime_group = 'Realtime REST User'
REST_GROUP = getattr(
    settings, 'REALTIME_REST_GROUP', default_realtime_group)

VOLCANO_GROUP = getattr(
    settings, 'VOLCANO_REALTIME_REST_GROUP', 'Volcano Realtime REST User')

ASH_GROUP = getattr(
    settings, 'ASH_REALTIME_REST_GROUP', 'Ash Realtime REST User')

default_language_list = [
    {'name': 'English', 'id': 'en'},
    {'name': 'Indonesia', 'id': 'id'},
]
LANGUAGE_LIST = getattr(
    settings, 'REALTIME_LANGUAGE_LIST', default_language_list)


# Realtime indicator
default_shake_interval_multiplier = {
    'healthy': 1,
    'warning': 2,
}

# indicates the range of interval between shake event to indicate that the
# reporting runs normally
SHAKE_INTERVAL_MULTIPLIER = getattr(
    settings, 'REALTIME_SHAKE_INTERVAL_MULTIPLIER',
    default_shake_interval_multiplier)

default_rest_interval_range = {
    'healthy': timedelta(minutes=5),
    'warning': timedelta(minutes=10)
}

# indicates the range of interval between shake event to indicate that the
# reporting runs normally
REST_INTERVAL_RANGE = getattr(
    settings, 'REALTIME_REST_INTERVAL_RANGE', default_rest_interval_range)


default_realtime_broker_interval_range = {
    'healthy': timedelta(minutes=5),
    'warning': timedelta(minutes=10)
}

# indicates the range of interval between Realtime broker connection tests to
# indicate that the connection is healthy
REALTIME_BROKER_INTERVAL_RANGE = getattr(
    settings, 'REALTIME_BROKER_INTERVAL_RANGE',
    default_realtime_broker_interval_range)

# URL to get BMKG's Felt Earthquake list
FELT_EARTHQUAKE_URL = 'http://bmkg.go.id/gempabumi/gempabumi-dirasakan.bmkg'

MAPQUEST_MAP_KEY = getattr(settings, 'MAPQUEST_MAP_KEY', '')

OSM_LEVEL_7_NAME = 'Kelurahan'

OSM_LEVEL_8_NAME = 'RW'
