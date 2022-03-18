# coding=utf-8
"""Model Admin Class."""
from builtins import str
from django.contrib import admin
from django.contrib.admin import ModelAdmin, StackedInline
from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.admin import GenericStackedInline
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from leaflet.admin import LeafletGeoAdmin

from realtime.forms.coreflatpage import CoreFlatPageForm
from realtime.forms.report_template import ReportTemplate
from realtime.models import EarthquakeMigration, FloodMigration
from realtime.models.ash import Ash, AshReport
from realtime.models.coreflatpage import CoreFlatPage
from realtime.models.earthquake import Earthquake, EarthquakeReport, \
    EarthquakeMMIContour
from realtime.models.flood import Boundary, Flood, FloodEventBoundary, \
    FloodReport
from realtime.models.impact import Impact
from realtime.models.volcano import Volcano


# Define a new FlatPageAdmin
class CoreFlatPageAdmin(FlatPageAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'slug_id',
                'url',
                'language',
                'title',
                'content',
                'group',
                'system_category',
                'order',
                'sites'
            )
        }),
    )
    list_display = (
        'title', 'url', 'language', 'group', 'system_category', 'order')
    form = CoreFlatPageForm


admin.site.unregister(FlatPage)
admin.site.register(CoreFlatPage, CoreFlatPageAdmin)


class RealtimeAdminSite(AdminSite):
    site_header = 'Realtime Model Administration'
    site_title = 'Realtime Admin'


realtime_admin_site = RealtimeAdminSite(name='realtime_admin')


class ImpactAdmin(ModelAdmin):
    """Admin Class for Impact Model."""
    list_display = (
        'id',
        'content_object_url_link',
        'content_type', 'language', 'impact_file_path', 'analysis_task_id',
        'analysis_task_status', 'analysis_task_result')

    def content_object_url_link(self, instance):
        return '<a href="{url}">{repr}</a>'.format(
            url=instance.content_object_url(),
            repr=str(instance.content_object))
    content_object_url_link.allow_tags = True


class ImpactInline(GenericStackedInline):
    """Inline Admin Class for Impact Model."""
    model = Impact
    extra = 0


class EarthquakeReportInline(StackedInline):
    """Inline Admin class for Earthquake Report Model."""
    exclude = ['report_image', 'report_thumbnail']
    model = EarthquakeReport
    extra = 0


class EarthquakeAdmin(LeafletGeoAdmin):
    """Admin Class for Earthquake Model."""
    list_display = (
        'shake_id', 'source_type', 'time', 'location_description',
        'magnitude', 'depth', 'push_task_status', 'push_task_result')
    list_filter = ('location_description', )
    search_fields = ['shake_id', 'location_description']
    inlines = [
        ImpactInline,
        EarthquakeReportInline,
    ]


class EarthquakeReportAdmin(ModelAdmin):
    """Admin Class for Earthquake Report Model."""
    list_display = ('earthquake', 'language', 'report_pdf',
                    'report_thumbnail')
    list_filter = ('earthquake__location_description', 'language')
    search_fields = ['earthquake__shake_id',
                     'earthquake__location_description']


class EarthquakeMMIContourAdmin(LeafletGeoAdmin):
    """Admin Class for Earthquake MMI Contour."""
    list_display = ('earthquake', 'mmi', 'properties')


class BoundaryAdmin(LeafletGeoAdmin):
    """Admin Class for Flood Boundary."""

    list_display = ('name', 'parent', 'boundary_alias')
    list_filter = ('name', 'parent', 'boundary_alias')
    search_fields = ['name', 'parent__name']


class FloodReportInline(StackedInline):
    """Inline Admin class for Flood Report Model."""
    model = FloodReport
    extra = 0


class FloodAdmin(ModelAdmin):
    """Admin Class for Flood Event."""
    list_display = (
        'event_id', 'data_source', 'time', 'total_affected',
        'boundary_flooded', 'push_task_status', 'push_task_result')

    inlines = [
        ImpactInline,
        FloodReportInline
    ]


class FloodEventBoundaryAdmin(ModelAdmin):
    list_display = ('flood', 'hazard_data')
    list_filter = ('flood', 'hazard_data')


class FloodReportAdmin(ModelAdmin):
    list_display = ('flood', 'language', 'impact_map')


class AshReportInline(StackedInline):
    """Inline Admin class for Ash Report Model."""
    model = AshReport
    extra = 0


class AshAdmin(ModelAdmin):
    """Admin class for Ash model"""
    list_display = (
        'volcano', 'alert_level', 'event_time',
        'event_time_zone_string', 'eruption_height',
        'forecast_duration', 'push_task_status', 'push_task_result')
    inlines = [
        ImpactInline,
        AshReportInline
    ]


class AshReportAdmin(ModelAdmin):
    """Admin class for Ash Report"""
    list_display = ('ash', 'language', 'report_map')


class VolcanoAdmin(LeafletGeoAdmin):
    """Admin class for volcano model"""
    list_display = (
        'volcano_name', 'location', 'elevation', 'province', 'district',
        'morphology')
    list_filter = ('province', 'district', 'morphology')
    search_fields = ['volcano_name', 'province', 'district', 'morphology']


class ReportTemplateAdmin(ModelAdmin):
    """Admin class for report template model"""
    list_display = ('hazard', 'language', 'version', 'timestamp')
    list_filter = ('hazard', 'language')


# Migration Admin Panel
class EarthquakeMigrationAdmin(ModelAdmin):
    """Admin class for EarthquakeMigration model"""
    list_display = [
        'event', 'migrated', 'has_shake_grid_in_raw_file',
        'has_shake_grid_in_media_file', 'has_shake_grid_in_database',
        'has_mmi_in_raw_file', 'has_mmi_in_media_file', 'has_mmi_in_database']
    list_filter = [
        'migrated', 'has_shake_grid_in_raw_file',
        'has_shake_grid_in_media_file', 'has_shake_grid_in_database',
        'has_mmi_in_raw_file', 'has_mmi_in_media_file', 'has_mmi_in_database']
    ordering = ['-event']


class FloodMigrationAdmin(ModelAdmin):
    """Admin class for FloodMigration model"""
    list_display = [
        'event', 'migrated', 'has_hazard_in_raw_file',
        'has_hazard_in_media_file', 'has_hazard_in_database',
        'has_impact_in_raw_file', 'has_impact_in_media_file',
        'has_impact_in_database']
    list_filter = [
        'migrated', 'has_hazard_in_raw_file',
        'has_hazard_in_media_file', 'has_hazard_in_database',
        'has_impact_in_raw_file', 'has_impact_in_media_file',
        'has_impact_in_database']
    ordering = ['-event']


realtime_admin_site.register(Impact, ImpactAdmin)
realtime_admin_site.register(Earthquake, EarthquakeAdmin)
realtime_admin_site.register(EarthquakeReport, EarthquakeReportAdmin)
realtime_admin_site.register(EarthquakeMMIContour, EarthquakeMMIContourAdmin)
realtime_admin_site.register(Boundary, BoundaryAdmin)
realtime_admin_site.register(Flood, FloodAdmin)
realtime_admin_site.register(FloodEventBoundary, FloodEventBoundaryAdmin)
realtime_admin_site.register(FloodReport, FloodReportAdmin)
realtime_admin_site.register(Ash, AshAdmin)
realtime_admin_site.register(AshReport, AshReportAdmin)
realtime_admin_site.register(Volcano, VolcanoAdmin)
realtime_admin_site.register(ReportTemplate, ReportTemplateAdmin)
realtime_admin_site.register(EarthquakeMigration, EarthquakeMigrationAdmin)
realtime_admin_site.register(FloodMigration, FloodMigrationAdmin)
