# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.views.i18n import javascript_catalog
from realtime.admin import realtime_admin_site


js_info_dict = {
    'packages': ('realtime',),
}

urlpatterns = patterns(
    '',

    url(r'^admin/', include(admin.site.urls)),

    # uncomment to enable defaut Django auth
    # url(r'^accounts/login/$', 'django.contrib.auth.views.login'),

    # include application urls
    url(r'', include('frontend.urls', namespace='front_end')),
    url(r'^user-map/', include('user_map.urls', namespace='user_map')),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict),
    url(r'^realtime/', include('realtime.urls', namespace='realtime')),
    url(r'^realtime/api-auth/', include('rest_framework.urls',
                                        namespace='rest_framework')),
    url(r'^realtime/admin/', include(realtime_admin_site.urls)),

    # url pattern for realtime reports
    url(r'', include('realtime.report_urls', namespace='realtime_report')),
)

# expose static files and uploded media if DEBUG is active
if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {
                'document_root': settings.MEDIA_ROOT,
                'show_indexes': True
            }),
        url(r'', include('django.contrib.staticfiles.urls'))
    )
