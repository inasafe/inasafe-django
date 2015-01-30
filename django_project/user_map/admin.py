# coding=utf-8
"""Model Admin Class."""

from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin

from user_map.models import User, InasafeRole, OsmRole


class UserAdmin(LeafletGeoAdmin):
    """Admin Class for User Model."""
    list_display = ('name', 'email', 'get_inasafe_roles',
                    'get_osm_roles', 'website', 'email_updates',
                    'last_login', 'is_confirmed', 'is_admin')
    list_filter = ['inasafe_roles', 'osm_roles', 'is_confirmed', 'is_admin']
    search_fields = ['name', 'email']
    fieldsets = [
        ('Basic Information', {
            'fields': [
                'name', 'email', 'website', 'inasafe_roles', 'osm_roles',
                'email_updates']}),
        ('Location', {'fields': ['location']}),
        ('Advanced Information', {
            'fields': ['is_confirmed', 'is_active', 'is_admin', 'last_login']
        }),
    ]


admin.site.register(User, UserAdmin)
admin.site.register(InasafeRole)
admin.site.register(OsmRole)
