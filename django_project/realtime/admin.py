# coding=utf-8
"""Model Admin Class."""
from django.contrib.admin.sites import AdminSite

from django.contrib.admin import ModelAdmin
from leaflet.admin import LeafletGeoAdmin

from realtime.models.earthquake import Earthquake, EarthquakeReport


class RealtimeAdminSite(AdminSite):
    site_header = 'Realtime Model Administration'
    site_title = 'Realtime Admin'


realtime_admin_site = RealtimeAdminSite(name='realtime_admin')


class EarthquakeAdmin(LeafletGeoAdmin):
    """Admin Class for Earthquake Model."""
    list_display = ('shake_id', 'time', 'location_description', 'magnitude',
                    'depth')
    list_filter = ('location_description', )
    search_fields = ['shake_id', 'location_description']


class EarthquakeReportAdmin(ModelAdmin):
    """Admin Class for Earthquake Report Model."""
    list_display = ('earthquake', 'language', 'report_pdf',
                    'report_thumbnail')
    list_filter = ('earthquake__location_description', 'language')
    search_fields = ['earthquake__shake_id',
                     'earthquake__location_description']


realtime_admin_site.register(Earthquake, EarthquakeAdmin)
realtime_admin_site.register(EarthquakeReport, EarthquakeReportAdmin)
