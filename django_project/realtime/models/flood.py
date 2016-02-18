# coding=utf-8
"""Model class for flood realtime."""

from django.contrib.gis.db import models


class BoundaryAlias(models.Model):
    """Aliases for Boundary"""
    class Meta:
        """Meta class"""
        app_label = 'realtime'

    alias = models.CharField(
        verbose_name='Alias of Boundary Level',
        help_text='Alternate or human readable name for boundary level',
        max_length=64)
    osm_level = models.IntegerField(
        verbose_name='OSM Boundary Level',
        help_text='OSM Equivalent of boundary level')
    parent = models.ForeignKey(
        'BoundaryAlias',
        verbose_name='Parent boundary alias',
        help_text='The parent of this boundary alias, it should also be a '
                  'boundary alias',
        blank=True,
        null=True)

    def __unicode__(self):
        return 'Osm level %s - %s' % (self.osm_level, self.alias)


class Boundary(models.Model):
    """Model for geographic boundaries"""
    class Meta:
        """Meta class"""
        app_label = 'realtime'
        verbose_name_plural = 'Boundaries'

    upstream_id = models.CharField(
        verbose_name='Upstream ID',
        help_text='ID used by upstream data source to identify boundaries',
        max_length=64,
        unique=True,
        blank=False)
    name = models.CharField(
        verbose_name='Boundary name',
        help_text='Name entitled to this particular boundary',
        max_length=64,
        blank=True,
        null=True)
    parent = models.ForeignKey(
        'Boundary',
        verbose_name='Parent boundary',
        help_text='The boundary parent of this particular boundary, if any. '
                  'This should also be a boundary.',
        blank=True,
        null=True)
    geometry = models.MultiPolygonField(
        verbose_name='Geometry of the boundary',
        help_text='Geometry of the boundary',
        blank=False)
    boundary_alias = models.ForeignKey(
        BoundaryAlias,
        verbose_name='Boundary level alias',
        help_text='The alias of boundary level of this boundary',
        blank=True,
        null=True)

    def __unicode__(self):
        return self.name


class Flood(models.Model):
    """Flood model."""
    class Meta:
        """Meta class."""
        app_label = 'realtime'

    event_id = models.CharField(
        verbose_name='The id of the event',
        help_text='The id of the event, which represents time and interval',
        max_length=20,
        unique=True,
        blank=False)
    time = models.DateTimeField(
        verbose_name='Date and Time',
        help_text='The time the flood reported.',
        blank=False)
    interval = models.IntegerField(
        verbose_name='Report interval',
        help_text='The interval of aggregated report in hours',
        default=0)
    source = models.CharField(
        verbose_name='Flood Data Source',
        help_text='The source of hazard data',
        max_length=255)
    region = models.CharField(
        verbose_name='The Region id for source',
        help_text='The region of hazard data',
        max_length=255)
    hazard_layer = models.FileField(
        blank=True,
        verbose_name='Hazard Layer',
        help_text='Zipped file of Hazard Layer related files',
        upload_to='reports/flood/zip')
    # impact_layer = models.FileField(
    #     blank=True,
    #     verbose_name='Impact Layer',
    #     help_text='Zipped file of Impact Layer related files',
    #     upload_to='reports/flood/zip')
    flooded_boundaries = models.ManyToManyField(
        Boundary,
        through='FloodEventBoundary',
        verbose_name='Flooded Boundaries',
        help_text='The linked boundaries flooded by this event')

    objects = models.GeoManager()

    def delete(self, using=None):
        # delete impact layer
        self.hazard_layer.delete()
        return super(Flood, self).delete(using=using)

    def __unicode__(self):
        return 'Flood event & interval: %s - %s' % (self.time, self.interval)


class FloodReport(models.Model):
    """Flood Report models"""

    class Meta:
        """Meta class"""
        app_label = 'realtime'
        unique_together = (('flood', 'language'), )

    flood = models.ForeignKey(
        Flood,
        related_name='reports')
    language = models.CharField(
        verbose_name='Language ID',
        help_text='The language ID of the report',
        max_length=4,
        default='id'
    )
    impact_report = models.FileField(
        blank=True,
        verbose_name='Impact Report',
        help_text='Impact Report file in PDF',
        upload_to='reports/flood/pdf')
    impact_map = models.FileField(
        blank=True,
        verbose_name='Impact Map',
        help_text='Impact Map file in PDF',
        upload_to='reports/flood/pdf')

    def delete(self, using=None):
        self.impact_report.delete()
        self.impact_map.delete()
        return super(FloodReport, self).delete(using=using)


class FloodEventBoundary(models.Model):
    """Flood Event Boundary model."""
    class Meta:
        app_label = 'realtime'
        unique_together = (('flood', 'boundary'), )

    flood = models.ForeignKey(
        Flood,
        to_field='event_id',
        verbose_name='Flood Event',
        help_text='The flood event of the linked boundary',
        related_name='flood_event')
    boundary = models.ForeignKey(
        Boundary,
        to_field='upstream_id',
        verbose_name='Boundary',
        help_text='The linked boundary of the flood events',
        related_name='flood_event')
    impact_data = models.IntegerField(
        verbose_name='Impact Data',
        help_text='Impact data in the given boundary',
        blank=True,
        null=True)


from realtime.signals.flood import *  # noqa
