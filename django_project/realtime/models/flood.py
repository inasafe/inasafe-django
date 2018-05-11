# coding=utf-8
"""Model class for flood realtime."""

from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from realtime.models.mixins import BaseEventModel
from realtime.models.report import BaseEventReportModel


class BoundaryAlias(models.Model):
    """Aliases for Boundary"""
    class Meta:
        """Meta class"""
        app_label = 'realtime'

    alias = models.CharField(
        verbose_name=_('Alias of Boundary Level'),
        help_text=_('Alternate or human readable name for boundary level'),
        max_length=64)
    osm_level = models.IntegerField(
        verbose_name=_('OSM Boundary Level'),
        help_text=_('OSM Equivalent of boundary level'))
    parent = models.ForeignKey(
        'BoundaryAlias',
        verbose_name=_('Parent boundary alias'),
        help_text=_('The parent of this boundary alias, it should also be a '
                    'boundary alias'),
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
        verbose_name=_('Upstream ID'),
        help_text=_('ID used by upstream data source to identify boundaries'),
        max_length=64,
        blank=False)
    name = models.CharField(
        verbose_name=_('Boundary name'),
        help_text=_('Name entitled to this particular boundary'),
        max_length=64,
        blank=True,
        null=True)
    parent = models.ForeignKey(
        'Boundary',
        verbose_name=_('Parent boundary'),
        help_text=_('The boundary parent of this particular boundary, if any. '
                    'This should also be a boundary.'),
        blank=True,
        null=True)
    geometry = models.MultiPolygonField(
        verbose_name=_('Geometry of the boundary'),
        help_text=_('Geometry of the boundary'),
        blank=False)
    boundary_alias = models.ForeignKey(
        BoundaryAlias,
        verbose_name=_('Boundary level alias'),
        help_text=_('The alias of boundary level of this boundary'),
        blank=True,
        null=True)

    def __unicode__(self):
        return self.name


class FloodManager(models.GeoManager):

    def get_queryset(self):
        return super(FloodManager, self).get_queryset().defer(
            'flood_data')


class Flood(BaseEventModel):
    """Flood model."""

    class Meta:
        """Meta class."""
        app_label = 'realtime'

    event_id = models.CharField(
        verbose_name=_('The id of the event'),
        help_text=_('The id of the event, which represents time and interval'),
        max_length=20,
        unique=True,
        blank=False)
    flood_data = models.TextField(
        verbose_name=_('Flood Data Contents'),
        help_text=_('The content of flood data in json format.'),
        blank=True,
        null=True)
    flood_data_saved = models.BooleanField(
        verbose_name=_('Cache flag to tell that flood_data is saved.'),
        default=False)
    data_source = models.CharField(
        verbose_name=_('The source of hazard data'),
        help_text=_('The source of the hazard data used for analysis'),
        max_length=255,
        blank=True,
        null=True,
        default=None)
    time = models.DateTimeField(
        verbose_name=_('Date and Time'),
        help_text=_('The time the flood reported.'),
        blank=False)
    interval = models.IntegerField(
        verbose_name=_('Report interval'),
        help_text=_('The interval of aggregated report in hours'),
        default=0)
    source = models.CharField(
        verbose_name=_('Flood Data Source'),
        help_text=_('The source of hazard data'),
        default=None,
        blank=True,
        null=True,
        max_length=255)
    region = models.CharField(
        verbose_name=_('The Region id for source'),
        help_text=_('The region of hazard data'),
        max_length=255)
    hazard_layer = models.FileField(
        blank=True,
        verbose_name=_('Hazard Layer'),
        help_text=_('Zipped file of Hazard Layer related files'),
        upload_to='reports/flood/zip')
    impact_layer = models.FileField(
        blank=True,
        verbose_name=_('Impact Layer'),
        help_text=_('Zipped file of Impact Layer related files'),
        upload_to='reports/flood/zip')
    flooded_boundaries = models.ManyToManyField(
        Boundary,
        through='FloodEventBoundary',
        verbose_name=_('Flooded Boundaries'),
        help_text=_('The linked boundaries flooded by this event'))
    total_affected = models.IntegerField(
        verbose_name=_('Total affected people by flood'),
        help_text=_('Total affected people by flood'),
        default=0)
    boundary_flooded = models.IntegerField(
        verbose_name=_('Total boundary flooded'),
        help_text=_('Total boundary affected by flood'),
        default=0)

    objects = FloodManager()

    def delete(self, using=None):
        # delete impact layer
        self.hazard_layer.delete()
        return super(Flood, self).delete(using=using)

    def __unicode__(self):
        return 'Flood event & interval: %s - %s' % (self.time, self.interval)

    @property
    def event_id_formatted(self):
        return self.event_id

    @property
    def reports_queryset(self):
        return self.reports

    @property
    def report_class(self):
        return FloodReport

    @property
    def flood_data_download_url(self):
        return reverse('realtime:flood_data', kwargs={
            'event_id': self.event_id,
        })


class FloodReport(BaseEventReportModel):
    """Flood Report models"""

    class Meta:
        """Meta class"""
        app_label = 'realtime'
        unique_together = (('flood', 'language'), )

    flood = models.ForeignKey(
        Flood,
        related_name='reports')
    impact_report = models.FileField(
        blank=True,
        verbose_name=_('Impact Report'),
        help_text=_('Impact Report file in PDF'),
        upload_to='reports/flood/pdf')
    impact_map = models.FileField(
        blank=True,
        verbose_name=_('Impact Map'),
        help_text=_('Impact Map file in PDF'),
        upload_to='reports/flood/pdf')

    @property
    def event(self):
        return self.flood

    @event.setter
    def event(self, value):
        self.flood = value

    @property
    def canonical_report_pdf(self):
        return self.impact_map

    @property
    def canonical_report_filename(self):
        return self.impact_map_filename

    @property
    def impact_report_url(self):
        """Return url friendly address for impact report pdf"""
        parameters = {
            'event_id': self.flood.event_id,
            'language': self.language
        }
        return reverse('realtime:flood_impact_report', kwargs=parameters)

    @property
    def impact_map_filename(self):
        """Return standardized filename for report map."""
        filename_format = '{event_id}_{language}.pdf'
        return filename_format.format(
            event_id=self.flood.event_id,
            language=self.language)

    @property
    def impact_map_url(self):
        """Return url friendly address for impact map pdf"""
        parameters = {
            'event_id': self.flood.event_id,
            'language': self.language
        }
        return reverse('realtime:flood_impact_map', kwargs=parameters)

    def delete(self, using=None):
        self.impact_report.delete()
        self.impact_map.delete()
        return super(FloodReport, self).delete(using=using)


class FloodEventBoundary(models.Model):
    """Flood Event Boundary model."""
    class Meta:
        app_label = 'realtime'
        unique_together = (('flood', 'boundary'), )
        verbose_name_plural = 'Flood Event Boundaries'

    flood = models.ForeignKey(
        Flood,
        to_field='event_id',
        verbose_name=_('Flood Event'),
        help_text=_('The flood event of the linked boundary'),
        related_name='flood_event')
    boundary = models.ForeignKey(
        Boundary,
        verbose_name=_('Boundary'),
        help_text=_('The linked boundary of the flood events'),
        related_name='flood_event')
    hazard_data = models.IntegerField(
        verbose_name=_('Impact Data'),
        help_text=_('Impact data in the given boundary'),
        blank=True,
        null=True)


class ImpactEventBoundary(models.Model):
    """Impact Event Boundary model."""
    class Meta:
        app_label = 'realtime'

    flood = models.ForeignKey(
        Flood,
        to_field='event_id',
        verbose_name=_('Flood Event'),
        help_text=_('The flood event of the linked boundary'),
        related_name='impact_event')
    parent_boundary = models.ForeignKey(
        Boundary,
        verbose_name=_('Boundary'),
        help_text=_('The linked parent boundary of the impact'),
        related_name='impact_event')
    geometry = models.MultiPolygonField(
        verbose_name=_('Geometry of the boundary of impact'),
        help_text=_('Geometry of the boundary of impact'),
        blank=False)
    affected = models.BooleanField(
        verbose_name=_('Affected status of the boundary impact'),
        help_text=_('Affected status of the boundary impact'),
        blank=False,
        null=False,
        default=False)
    hazard_class = models.CharField(
        verbose_name=_('Hazard Class'),
        help_text=_('Hazard class in the given boundary'),
        max_length=50,
        blank=True,
        null=True)
    population_affected = models.IntegerField(
        verbose_name=_('Population Affected'),
        help_text=_('The affected population in a given flood boundary'),
        blank=True,
        null=True)


from realtime.signals.flood import *  # noqa
