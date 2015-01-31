# -*- coding: utf-8 -*-
from .base import *  # noqa

# Extra installed apps
INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',  # enable Raven plugin
    'pipeline',
    'user_map',
    'leaflet',
    'bootstrapform'
)

# define template function (example for underscore)
# PIPELINE_TEMPLATE_FUNC = '_.template'

# define template function (example for underscore)
# PIPELINE_TEMPLATE_FUNC = '_.template'
PIPELINE_YUI_BINARY = '/usr/bin/yui-compressor'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
PIPELINE_YUI_JS_ARGUMENTS = '--nomunge'
PIPELINE_DISABLE_WRAPPER = True
# enable cached storage - requires uglify.js (node.js)
STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
MIDDLEWARE_CLASSES += (
   'django.middleware.gzip.GZipMiddleware',
   'pipeline.middleware.MinifyHTMLMiddleware',
)


# User map sets up auth where users are identified by their email,
# not by their user name.
AUTH_USER_MODEL = 'user_map.User'
AUTHENTICATION_BACKENDS = [
    'user_map.auth_backend.UserMapAuthBackend',
    'django.contrib.auth.backends.ModelBackend']


TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'user_map.context_processors.user_map_settings',
)

LEAFLET_CONFIG = {
    'TILES': [
        (
            'OpenStreetMap',
            'http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
            ('© <a href="http://www.openstreetmap.org" '
             'target="_parent">OpenStreetMap</a> and contributors, under an '
             '<a href="http://www.openstreetmap.org/copyright" '
             'target="_parent">open license</a>')
        )]

}
