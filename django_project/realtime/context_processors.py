# coding=utf-8
"""Module for custom context processor for InaSAFE Realtime."""
from realtime import app_settings
from realtime.app_settings import (
    LANGUAGE_LIST,
    LEAFLET_TILES,
    MAPQUEST_MAP_KEY)
from realtime.models.coreflatpage import CoreFlatPage


def realtime_settings(request):
    """Add media configuration for user map e.g favicon path so that we can
    use it directly on template.

    :param request: A django request object.
    :type request: request
    """

    # language related
    selected_language = {
        'id': 'en',
        'name': 'English'
    }
    language_code = 'en'
    if request.method == 'GET':
        if 'lang' in request.GET:
            language_code = request.GET.get('lang')
    for l in LANGUAGE_LIST:
        if l['id'] == language_code:
            selected_language = l

    language_list = [l for l in LANGUAGE_LIST if not l['id'] == language_code]

    # Leaflet context
    leaflet_tiles = []
    for i in range(0, len(LEAFLET_TILES[1])):
        leaflet_tiles.append(
            dict(
                name=LEAFLET_TILES[0][i],
                url=LEAFLET_TILES[1][i],
                subdomains=LEAFLET_TILES[2][i],
                attribution=LEAFLET_TILES[3][i]
            )
        )

    # Check Navbar flat pages exists and show it
    # Get distinct Groups
    groups = CoreFlatPage.objects.order_by().values_list('group')\
        .distinct()
    flatpages = {
        'groups': []
    }
    for g in groups:
        group = {
            'title': g[0],
            'pages': []
        }
        pages = CoreFlatPage.objects.filter(group__iexact=g).order_by('order')
        for p in pages:
            page = {
                'title': p.title,
                'url': p.url
            }
            group['pages'].append(page)
        flatpages['groups'].append(group)

    return {
        'REALTIME_PROJECT_NAME': app_settings.PROJECT_NAME,
        'REALTIME_BRAND_LOGO': app_settings.BRAND_LOGO,
        'REALTIME_FAVICON_PATH': app_settings.FAVICON_FILE,
        'flatpages': flatpages,
        'leaflet_tiles': leaflet_tiles,
        'mapquest_key': MAPQUEST_MAP_KEY,
        'language': {
            'selected_language': selected_language,
            'language_list': language_list,
        }
    }
