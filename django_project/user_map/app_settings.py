# coding=utf-8
"""Configurations file for User Map.

..note: By design, you can override these settings from your project's
    settings.py with prefix 'USER_MAP' on the variable e.g
    'USER_MAP_USER_ICONS'.

    For mailing. as the default, it wil use 'DEFAULT_FROM_MAIL' setting from
    the project.
"""
from django.conf import settings

# PROJECT_NAME: The project name for this apps e.g InaSAFE
default_project_name = 'InaSAFE'
PROJECT_NAME = getattr(settings, 'USER_MAP_PROJECT_NAME', default_project_name)

# LOGO/BRAND
default_brand_logo = 'user_map/img/logo.png'
BRAND_LOGO = getattr(settings, 'USER_MAP_BRAND_LOGO', default_brand_logo)

# FAVICON_FILE: Favicon for this apps
default_favicon_file = 'user_map/img/inasafe-icon.png'
FAVICON_FILE = getattr(settings, 'USER_MAP_FAVICON_FILE', default_favicon_file)

# PROJECTS
default_projects = [
    dict(
        name='InaSAFE',
        icon='user_map/img/inasafe-icon.png',
        shadow_icon='user_map/img/shadow-icon.png'),
    dict(
        name='OpenStreetMap',
        icon='user_map/img/osm-icon.png',
        shadow_icon='user_map/img/shadow-icon.png')]
PROJECTS = getattr(
    settings, 'USER_MAP_PROJECTS', default_projects)

# ROLES: All roles and their badges
default_inasafe_roles = [
    dict(
        name='User',
        badge='user_map/img/inasafe-badge-user.png'),
    dict(
        name='Trainer',
        badge='user_map/img/inasafe-badge-trainer.png'),
    dict(
        name='Developer',
        badge='user_map/img/inasafe-badge-developer.png')]
INASAFE_ROLES = getattr(
    settings, 'USER_MAP_INASAFE_ROLES', default_inasafe_roles)

INASAFE_CERTIFIED_TRAINER_BADGE = getattr(
    settings,
    'USER_MAP_INASAFE_CERTIFIED_TRAINER_BADGE',
    'user_map/img/inasafe-badge-certified-trainer.png'
)

default_osm_roles = [
    dict(
        name='Mapper',
        badge='user_map/img/osm-badge-mapper.png'),
    dict(
        name='Trainer',
        badge='user_map/img/osm-badge-trainer.png')]
OSM_ROLES = getattr(settings, 'USER_MAP_OSM_ROLES', default_osm_roles)

OSM_CERTIFIED_TRAINER_BADGE = getattr(
    settings,
    'USER_MAP_OSM_CERTIFIED_TRAINER_BADGE',
    'user_map/img/osm-badge-certified-trainer.png'
)

# MAIL SENDER
default_mail_sender = 'noreply@inasafe.org'
DEFAULT_FROM_MAIL = getattr(settings, 'DEFAULT_FROM_MAIL', default_mail_sender)

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
