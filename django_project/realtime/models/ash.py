# coding=utf-8
"""Model class for ash realtime."""
import os

import pytz
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from realtime.app_settings import ASH_EVENT_ID_FORMAT, ASH_EVENT_REPORT_FORMAT
from realtime.models.volcano import Volcano

__author__ = 'ismailsunni'
__project_name__ = 'inasafe-django'
__filename__ = 'ash'
__date__ = '7/15/16'
__copyright__ = 'imajimatika@gmail.com'


class Ash(models.Model):
    """Ash model."""
    class Meta:
        """Meta class."""
        app_label = 'realtime'
        verbose_name_plural = 'Ashes'

    volcano = models.ForeignKey(
        Volcano,
        related_name='ash',
        null=True)
    alert_level = models.CharField(
        verbose_name=_('Alert Level'),
        help_text=_('The alert level of the volcano ash event.'),
        max_length='30',
        blank=False
    )
    hazard_file = models.FileField(
        verbose_name=_('Hazard File'),
        help_text=_('Hazard file formatted as GeoTIFF (*.tif) in EPSG:4326.'),
        upload_to='ash/hazard_file/%Y/%m/%d',
        blank=False
    )
    impact_files = models.FileField(
        verbose_name=_('Impact Files'),
        help_text=_('Impact files processed zipped'),
        upload_to='ash/impact_files/%Y/%m/%d',
        blank=True,
        null=True
    )
    event_time = models.DateTimeField(
        verbose_name=_('Event Date and Time'),
        help_text=_('The time the ash happened.'),
        blank=False)
    event_time_zone_offset = models.IntegerField(
        verbose_name=_('Time Zone Offset'),
        help_text=_('The time zone offset of event time.'),
        default=0)
    event_time_zone_string = models.CharField(
        verbose_name=_('Time Zone String'),
        help_text=_('The time zone string of event time.'),
        max_length=255,
        blank=False,
        default='UTC')
    eruption_height = models.IntegerField(
        verbose_name=_(
            'Eruption height in metres. Calculated from the vent height'),
        blank=False,
        default=0)
    forecast_duration = models.IntegerField(
        verbose_name=_('Duration of forecast for Ash Hazard in days'),
        default=1)
    task_id = models.CharField(
        verbose_name=_('Celery task id'),
        help_text=_('Task id for processing'),
        max_length=255,
        default='',
        blank=True)
    task_status = models.CharField(
        verbose_name=_('Celery task status'),
        help_text=_('Task status for processing'),
        max_length=30,
        default='None',
        blank=True)
    hazard_path = models.CharField(
        verbose_name=_('Hazard Layer path'),
        help_text=_('Location of hazard layer'),
        max_length=255,
        default=None,
        blank=True)
    inasafe_version = models.CharField(
        verbose_name=_('InaSAFE version'),
        help_text=_('InaSAFE version being used'),
        max_length=10,
        default=None,
        blank=True)

    objects = models.GeoManager()

    def __unicode__(self):
        ash_event = u'Ash event of [%s] [%s]' % (
            self.volcano, self.event_time)
        return ash_event

    def __init__(self, *args, **kwargs):
        super(Ash, self).__init__(*args, **kwargs)
        self.use_timezone()

    def use_timezone(self):
        """Use saved timezone information for event_time"""
        # Reformat event_time with timezone
        try:
            tz = pytz.timezone(self.event_time_zone_string)
            self.event_time = self.event_time.astimezone(tz)
        except BaseException:
            pass

    @property
    def event_id_formatted(self):
        return ASH_EVENT_ID_FORMAT.format(
            event_time=self.event_time,
            volcano_name=self.volcano.volcano_name)

    def delete(self, using=None):
        # delete all report
        if self.hazard_file:
            self.hazard_file.delete()
        if self.impact_files:
            self.impact_files.delete()
        return super(Ash, self).delete(using=using)

    @property
    def hazard_layer_exists(self):
        """Return bool to indicate existances of hazard layer"""
        if self.hazard_path:
            return os.path.exists(self.hazard_path)
        return False


class AshReport(models.Model):
    """Ash Report Model."""

    class Meta:
        app_label = 'realtime'
        unique_together = (('ash', 'language'), )

    ash = models.ForeignKey(
        Ash,
        related_name='reports')
    language = models.CharField(
        verbose_name=_('Language ID'),
        help_text=_('The language ID of the report'),
        max_length=4,
        default='en'
    )
    report_map = models.FileField(
        verbose_name=_('Map PDF Report'),
        help_text=_('The map impact report stored as PDF'),
        upload_to='reports/ash/pdf'
    )

    @property
    def report_map_filename(self):
        """Return standardized filename for report map."""
        return ASH_EVENT_REPORT_FORMAT.format(
            event_time=self.ash.event_time,
            volcano_name=self.ash.volcano.volcano_name,
            language=self.language)

    @property
    def report_map_url(self):
        """Return url friendly address for report map"""
        event_time_format = '%Y%m%d%H%M%S%z'
        parameters = {
            'volcano_name': self.ash.volcano.volcano_name,
            'event_time': self.ash.event_time.strftime(event_time_format),
            'language': self.language
        }
        return reverse('realtime:ash_report_map', kwargs=parameters)

    def delete(self, using=None):
        self.report_map.delete()
        return super(AshReport, self).delete(using=using)
