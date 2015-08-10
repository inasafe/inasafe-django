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
default_brand_logo = 'realtime/img/logo.png'
BRAND_LOGO = getattr(settings, 'REALTIME_BRAND_LOGO', default_brand_logo)

# FAVICON_FILE: Favicon for this apps
default_favicon_file = 'realtime/img/favicon.ico'
FAVICON_FILE = getattr(settings, 'REALTIME_FAVICON_FILE',
                       default_favicon_file)


# LEAFLET CONFIG
default_leaflet_tiles = (
    ['MapQuest',
     'OpenStreetMap',
     ],
    [
        'http://otile{s}.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.png',
        'http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
    ],
    [
        '1234',
        'abcd',
    ],
    ['© <a href="http://www.openstreetmap.org" target="_parent">OpenStreetMap'
     '</a> and contributors, under an <a '
     'href="http://www.openstreetmap.org/copyright" target="_parent">open '
     'license</a>. Tiles Courtesy of <a '
     'href="http://www.mapquest.com/">MapQuest</a> <img '
     'src="http://developer.mapquest.com/content/osm/mq_logo.png"',
     '© <a href="http://www.openstreetmap.org" target="_parent">OpenStreetMap'
     '</a> and contributors, under an <a '
     'href="http://www.openstreetmap.org/copyright" target="_parent">open '
     'license</a>.',
     ]
)
LEAFLET_TILES = getattr(settings, 'LEAFLET_TILES', default_leaflet_tiles)

# Realtime Group:
default_realtime_group = 'Realtime REST User'
REST_GROUP = getattr(
    settings, 'REALTIME_REST_GROUP', default_realtime_group)

# Project Header
default_project_header = (
    """
    This page contains near realtime earthquake impact assessments
    following recent earthquakes in the Indonesia region.
    Shakemaps of earthquake ground shaking are produced by the
    Indonesian Agency for Meteorology, Climatology and Geophysics (BMKG)
    and used by the Indonesian National Disaster Management Agency (BNPB)
    to produce InaSAFE impact assessments within minutes of an earthquake
    (<a href="http://www.bnpb.go.id">http://www.bnpb.go.id</a>
    or <a href="http://realtime.inasafe.org">http://realtime.inasafe.org</a>).
    This information is used by disaster managers to help them understand
    the potential scale of a disaster and to respond faster to the
    hardest hit communities. This is particularly important in the
    first few hours after a large earthquake when it may be difficult
    to get accurate on-the-ground information.""")
PROJECT_HEADER = getattr(
    settings, 'REALTIME_PROJECT_HEADER', default_project_header)


# Project Header
default_project_credit = (
    """
    <div class="col-md-4">
        <h2>Supporters</h2>
        <p>Funded and supported by the
            <a href="http://www.aifdr.org/">Australia-Indonesia Facility
                for Disaster Reduction</a>,
            <a href="http://www.ga.gov.au/">Geoscience Australia</a> and
            the <a href="http://www.gfdrr.org">World Bank-GFDRR</a>.
        </p>
    </div>
    <div class="col-md-4">
        <h2>Partners</h2>

        <p>This software was developed with our partners in Indonesia:
            <a href="http://bnpb.go.id">Badan Nasional
                Penanggulangan Bencana (BNPB)</a> and
            <a href="http://www.bmkg.go.id">Badan Meteorologi, Klimatologi, dan
                Geofisika (BMKG)</a>
        </p>
    </div>
    <div class="span4">
        <h2>InaSAFE</h2>

        <p>This software is part of the
            <a href="http://inasafe.org">InaSAFE</a> project.
        </p>
    </div>
    """)
PROJECT_CREDIT = getattr(
    settings, 'REALTIME_PROJECT_CREDIT', default_project_credit)


default_language_list = [
    {'name': 'English', 'id': 'en'},
    {'name': 'Indonesia', 'id': 'id'},
]
LANGUAGE_LIST = getattr(
    settings, 'REALTIME_LANGUAGE_LIST', default_language_list)
