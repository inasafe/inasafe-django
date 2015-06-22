# coding=utf-8
from django.conf.urls import url
from realtime.views import earthquake
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import patterns, url

urlpatterns = [
    url(r'^api/v1/earthquake/$',
        earthquake.earthquake_list,
        name='earthquake_list'),
    url(r'^api/v1/earthquake/(?P<shake_id>[-\w]+)/$',
        earthquake.earthquake_detail,
        name='earthquake_detail'),
    url(r'^$', 'realtime.views.index', name='index'),
    url(r'^get_earthquakes/.*$', 'realtime.views.get_earthquakes', name='get_earthquakes'),
]

urlpatterns = format_suffix_patterns(urlpatterns)

