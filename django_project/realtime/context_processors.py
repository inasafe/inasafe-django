# coding=utf-8
"""Module for custom context processor for InaSAFE Realtime."""
from realtime import app_settings


def realtime_settings(request):
    """Add media configuration for user map e.g favicon path so that we can
    use it directly on template.

    :param request: A django request object.
    :type request: request
    """
    return {
        'REALTIME_PROJECT_NAME': app_settings.PROJECT_NAME,
        'REALTIME_BRAND_LOGO': app_settings.BRAND_LOGO,
        'REALTIME_FAVICON_PATH': app_settings.FAVICON_FILE,
    }
