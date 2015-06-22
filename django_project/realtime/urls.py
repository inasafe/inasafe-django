# coding=utf-8
from django.conf.urls import url
from realtime.views import earthquake
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^api/v1/earthquake/$', earthquake.earthquake_list),
    url(r'^api/v1/earthquake/(?P<shake_id>[-\w]+)/$',
        earthquake.earthquake_detail)
]

urlpatterns = format_suffix_patterns(urlpatterns)
