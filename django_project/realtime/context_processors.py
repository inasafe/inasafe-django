# coding=utf-8
"""Module for custom context processor for InaSAFE Realtime."""
from realtime import app_settings
from realtime.app_settings import (
    LEAFLET_TILES,
    MAPQUEST_MAP_KEY, ASH_SHOW_PAGE, OTHER_PAGE_SYSTEM_CATEGORY,
    ABOUT_PAGE_SYSTEM_CATEGORY)
from realtime.models.coreflatpage import CoreFlatPage


def realtime_settings(request):
    """Add media configuration for user map e.g favicon path so that we can
    use it directly on template.

    :param request: A django request object.
    :type request: request
    """

    def _protocol_check(url, is_secure):
        """Change protocol to https if secure"""
        if is_secure and 'http://' in url:
            return url.replace('http://', 'https://')
        return url

    # Leaflet context
    leaflet_tiles = []
    for i in range(0, len(LEAFLET_TILES[1])):
        leaflet_tiles.append(
            dict(
                name=LEAFLET_TILES[0][i],
                url=_protocol_check(LEAFLET_TILES[1][i], request.is_secure()),
                subdomains=LEAFLET_TILES[2][i],
                attribution=LEAFLET_TILES[3][i]
            )
        )

    # Check Navbar flat pages exists and show it
    # Get distinct Groups
    def retrieve_flat_pages(system_category):
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
            pages = CoreFlatPage.objects.filter(
                group__iexact=g,
                system_category=system_category,
                language=request.LANGUAGE_CODE
            ).order_by('order')
            # for p in pages:
            #     page = {
            #         'ic': p.id,
            #         'title': p.title,
            #         'url': p.url
            #     }
            #     group['pages'].append(page)
            group['pages'] = pages
            if pages:
                flatpages['groups'].append(group)

        return flatpages

    flatpages = retrieve_flat_pages(OTHER_PAGE_SYSTEM_CATEGORY)
    abouts = retrieve_flat_pages(ABOUT_PAGE_SYSTEM_CATEGORY)
    additional_nav_menus = [abouts, flatpages]

    return {
        'REALTIME_PROJECT_NAME': app_settings.PROJECT_NAME,
        'REALTIME_BRAND_LOGO': app_settings.BRAND_LOGO,
        'REALTIME_FAVICON_PATH': app_settings.FAVICON_FILE,
        # 'abouts': abouts,
        # 'flatpages': flatpages,
        'additional_nav_menus': additional_nav_menus,
        'leaflet_tiles': leaflet_tiles,
        'mapquest_key': MAPQUEST_MAP_KEY,
        'ASH_SHOW_PAGE': ASH_SHOW_PAGE
    }
