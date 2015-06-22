# coding=utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns(
    '', url(r'^$', 'realtime.views.index', name='index'),
    url(r'^get_earthquakes/.*$', 'realtime.views.get_earthquakes', name='get_earthquakes'),
)
