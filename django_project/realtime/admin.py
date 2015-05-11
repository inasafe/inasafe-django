# coding=utf-8
"""Model Admin Class."""

from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin

from .models.earthquake import Earthquake


class EarthquakeAdmin(LeafletGeoAdmin):
    """Admin Class for User Model."""
    list_display = ('shake_id', 'time', 'location_description', 'magnitude',
                    'depth')
    search_fields = ['shake_id', 'location_description']

admin.site.register(Earthquake, EarthquakeAdmin)
