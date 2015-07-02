# coding=utf-8
"""Configurations file for Realtime.

..note: By design, you can override these settings from your project's
    settings.py with prefix 'REALTIME' on the variable e.g
    'REALTIME_USER_ICONS'.

    For mailing. as the default, it wil use 'DEFAULT_FROM_MAIL' setting from
    the project.
"""
from django.conf import settings

# PROJECT_NAME: The project name for this apps e.g InaSAFE
default_project_name = 'InaSAFE'
PROJECT_NAME = getattr(settings, 'REALTIME_PROJECT_NAME',
                       default_project_name)

# LOGO/BRAND
default_brand_logo = 'REALTIME/img/logo.png'
BRAND_LOGO = getattr(settings, 'REALTIME_BRAND_LOGO', default_brand_logo)

# FAVICON_FILE: Favicon for this apps
default_favicon_file = 'REALTIME/img/inasafe-icon.png'
FAVICON_FILE = getattr(settings, 'REALTIME_FAVICON_FILE',
                       default_favicon_file)


# LEAFLET CONFIG
default_leaflet_tiles = (
    'OpenStreetMap',
    'http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
    ('© <a href="http://www.openstreetmap.org" target="_parent">OpenStreetMap'
     '</a> and contributors, under an <a '
     'href="http://www.openstreetmap.org/copyright" target="_parent">open '
     'license</a>')
)
LEAFLET_TILES = getattr(settings, 'LEAFLET_TILES', default_leaflet_tiles)
