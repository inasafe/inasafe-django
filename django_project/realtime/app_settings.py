# coding=utf-8
"""Configurations file for Realtime.

..note: By design, you can override these settings from your project's
    settings.py with prefix 'REALTIME' on the variable e.g
    'REALTIME_USER_ICONS'.

    For mailing. as the default, it wil use 'DEFAULT_FROM_MAIL' setting from
    the project.
"""
import ast
from datetime import timedelta

import os

import errno
from django.conf import settings

LOGGER_NAME = 'InaSAFE Realtime REST Server'

ON_TRAVIS = ast.literal_eval(os.environ.get('ON_TRAVIS', 'False'))
REALTIME_GEONODE_ENABLE = ast.literal_eval(
    os.environ.get('REALTIME_GEONODE_ENABLE', 'False'))

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


LANDING_PAGE_SYSTEM_CATEGORY = 'landing_page'
ABOUT_PAGE_SYSTEM_CATEGORY = 'about_page'
OTHER_PAGE_SYSTEM_CATEGORY = 'other'

FLATPAGE_SYSTEM_CATEGORY = (
    (LANDING_PAGE_SYSTEM_CATEGORY, LANDING_PAGE_SYSTEM_CATEGORY),
    (ABOUT_PAGE_SYSTEM_CATEGORY, ABOUT_PAGE_SYSTEM_CATEGORY),
    (OTHER_PAGE_SYSTEM_CATEGORY, OTHER_PAGE_SYSTEM_CATEGORY),
)


SLUG_EQ_LANDING_PAGE = 'eq_landing_page'
SLUG_FLOOD_LANDING_PAGE = 'flood_landing_page'
SLUG_ASH_LANDING_PAGE = 'ash_landing_page'

SLUG_EQ_ABOUT_PAGE = 'eq_about_page'
SLUG_FLOOD_ABOUT_PAGE = 'flood_about_page'
SLUG_ASH_ABOUT_PAGE = 'ash_about_page'

FLATPAGE_SYSTEM_SLUG_IDS = (
    (SLUG_EQ_LANDING_PAGE, SLUG_EQ_LANDING_PAGE),
    (SLUG_ASH_LANDING_PAGE, SLUG_ASH_LANDING_PAGE),
    (SLUG_FLOOD_LANDING_PAGE, SLUG_FLOOD_LANDING_PAGE),

    (SLUG_EQ_ABOUT_PAGE, SLUG_EQ_ABOUT_PAGE),
    (SLUG_ASH_ABOUT_PAGE, SLUG_ASH_ABOUT_PAGE),
    (SLUG_FLOOD_ABOUT_PAGE, SLUG_FLOOD_ABOUT_PAGE),
)


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

# Hazard Drop location
REALTIME_HAZARD_DROP = os.environ.get(
    'REALTIME_HAZARD_DROP',
    '/home/realtime/hazard-drop/')

try:
    os.makedirs(REALTIME_HAZARD_DROP)
except OSError as e:
    if not e.errno == errno.EEXIST:
        raise

# ASH Report Event ID Format
ASH_EVENT_TIME_FORMAT = getattr(
    settings,
    'ASH_EVENT_TIME_FORMAT',
    '{event_time:%Y%m%d%H%M%S%z}')
ASH_EVENT_ID_FORMAT = getattr(
    settings,
    'ASH_EVENT_ID_FORMAT',
    '{event_time:%Y%m%d%H%M%z}_{volcano_name}')
ASH_EVENT_REPORT_FORMAT = getattr(
    settings,
    'ASH_EVENT_REPORT_FORMAT',
    '{event_time:%Y%m%d%H%M%z}_{volcano_name}-{language}.pdf')

# ASH landing page toggle
ASH_SHOW_PAGE = os.environ.get(
    'ASH_SHOW_PAGE',
    'True')

if ASH_SHOW_PAGE:
    ASH_SHOW_PAGE = ast.literal_eval(ASH_SHOW_PAGE)
else:
    ASH_SHOW_PAGE = True

# Ash analysis contexts

ASH_EXPOSURES = [
    # Airport data
    '/home/headless/contexts/common/exposure/idn_places_wgs84.shp',

    # Disable this one first, to avoid duplicate exposures
    # Place data
    # '/home/headless/contexts/common/exposure/'
    # 'IDN_Capital_Population_Point_WGS84.shp',

    # Raster population data
    '/home/headless/contexts/common/exposure/idn_population_200m_wgs84.tif',

    # Landcover data
    '/home/headless/contexts/ash/exposure/idn_landcover_250k_wgs84.shp',
]
ASH_AGGREGATION = None
ASH_REPORT_TEMPLATE_EN = (
    '/home/headless/qgis-templates/volcanic-ash/realtime-ash-en.qpt')
ASH_REPORT_TEMPLATE_ID = (
    '/home/headless/qgis-templates/volcanic-ash/realtime-ash-id.qpt')
ASH_LAYER_ORDER = [

    # Volcano Crater
    '/home/headless/contexts/ash/context/idn_volcano_wgs84.shp',

    # Airport data and cities
    '/home/headless/contexts/common/exposure/idn_places_wgs84.shp',

    # the ash layer will be inserted in the method
    '@hazard',

    # terrain data
    '/home/headless/contexts/ash/context/idn_hillshade_wgs84.tif',
]
VOLCANO_LAYER_PATH = (
    '/home/web/django_project/realtime/fixtures/ash/idn_volcano_wgs84.shp')

# Earthquake analysis contexts

GRID_FILE_DEFAULT_NAME = 'grid.xml'

EARTHQUAKE_EXPOSURES = [
    # Population raster
    '/home/headless/contexts/common/exposure/idn_population_200m_wgs84.tif',

    # Cities
    '/home/headless/contexts/common/exposure/idn_places_wgs84.shp',

]
EARTHQUAKE_AGGREGATION = ''
EARTHQUAKE_REPORT_TEMPLATE_EN = (
    '/home/headless/qgis-templates/earthquake/realtime-earthquake-en.qpt')
EARTHQUAKE_REPORT_TEMPLATE_ID = (
    '/home/headless/qgis-templates/earthquake/realtime-earthquake-id.qpt')
EARTHQUAKE_LAYER_ORDER = [
    # Cities
    '/home/headless/contexts/common/exposure/idn_places_wgs84.shp',

    # MMI Contour
    '@population.earthquake_contour',

    # Administration boundary
    '/home/headless/contexts/common/context/idn_admin_boundaries_wgs84.shp',

    # Population layer
    '/home/headless/contexts/common/exposure/idn_population_200m_wgs84.tif',
]

EARTHQUAKE_EVENT_ID_FORMAT = getattr(
    settings,
    'EARTHQUAKE_EVENT_ID_FORMAT',
    '{shake_id}-{source_type}'
)

EARTHQUAKE_EVENT_REPORT_FORMAT = getattr(
    settings,
    'EARTHQUAKE_EVENT_REPORT_FORMAT',
    '{shake_id}-{source_type}-{language}{suffix}.{extension}')

EARTHQUAKE_MONITORED_DIRECTORY = os.environ.get(
    'EARTHQUAKE_MONITORED_DIRECTORY',
    '/home/realtime/shakemaps')

EARTHQUAKE_CORRECTED_MONITORED_DIRECTORY = os.environ.get(
    'EARTHQUAKE_CORRECTED_MONITORED_DIRECTORY',
    '/home/realtime/shakemaps-corrected')

# Flood analysis contexts

FLOOD_EXPOSURE = (
    # Jakarta population
    '/home/headless/contexts/flood/exposure/dki_jakarta_population_wgs84.shp')
FLOOD_AGGREGATION = (
    '/home/headless/contexts/'
    'flood/aggregation/dki_jakarta_admin_village.shp')
FLOOD_REPORT_TEMPLATE_EN = (
    '/home/headless/qgis-templates/flood/realtime-flood-en.qpt')
FLOOD_REPORT_TEMPLATE_ID = (
    '/home/headless/qgis-templates/flood/realtime-flood-id.qpt')
FLOOD_LAYER_ORDER = [

    # Displaced population with circle symbology
    '/home/headless/contexts/'
    'flood/aggregation/dki_jakarta_admin_village.shp',

    # Mask vector layer
    '/home/headless/contexts/flood/context/dki_jakarta_mask_wgs84.shp',

    # the flood layer will be inserted in the method
    '@hazard',

    # Administration boundary
    '/home/headless/contexts/common/context/idn_admin_boundaries_wgs84.shp',

    # OSM Basemap
    '/home/headless/contexts/flood/context/jakarta.jpg'
]

FLOOD_MONITORED_DIRECTORY = os.environ.get(
    'EARTHQUAKE_MONITORED_DIRECTORY',
    '/home/realtime/shakemaps')

# Report template contexts

ANALYSIS_LANGUAGES = ['en', 'id']

EARTHQUAKE_HAZARD_TYPE = 'earthquake'
FLOOD_HAZARD_TYPE = 'flood'
ASH_HAZARD_TYPE = 'ash'

HAZARD_TEMPLATE_TYPES = [
    EARTHQUAKE_HAZARD_TYPE, FLOOD_HAZARD_TYPE, ASH_HAZARD_TYPE]

HAZARD_TEMPLATE_CHOICES = [
    (t, t) for t in HAZARD_TEMPLATE_TYPES
]

REPORT_TEMPLATES = {
    'ash': {
        'en': ASH_REPORT_TEMPLATE_EN,
        'id': ASH_REPORT_TEMPLATE_ID
    },
    'earthquake': {
        'en': EARTHQUAKE_REPORT_TEMPLATE_EN,
        'id': EARTHQUAKE_REPORT_TEMPLATE_ID
    },
    'flood': {
        'en': FLOOD_REPORT_TEMPLATE_EN,
        'id': FLOOD_REPORT_TEMPLATE_ID
    }
}
