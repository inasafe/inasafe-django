# coding=utf-8
"""Model class for ash realtime."""

from builtins import object
import pytz
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from realtime.app_settings import ASH_EVENT_ID_FORMAT, \
    ASH_EVENT_REPORT_FORMAT, ASH_EVENT_TIME_FORMAT
from realtime.models.mixins import BaseEventModel
from realtime.models.report import BaseEventReportModel
from realtime.models.volcano import Volcano

__author__ = 'ismailsunni'
__project_name__ = 'inasafe-django'
__filename__ = 'ash'
__date__ = '7/15/16'
__copyright__ = 'imajimatika@gmail.com'


class Ash(BaseEventModel):
    """Ash model."""

    class Meta(object):
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
            'Eruption height in metres (above vent height)'),
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

    push_task_status = models.CharField(
        verbose_name=_('GeoNode Push Task Status'),
        help_text=_('The Status for the GeoNode Push Task'),
        max_length=255,
        default=None,
        null=True,
        blank=True)

    push_task_result = models.TextField(
        verbose_name=_('Report push task result'),
        help_text=_('Task result of GeoNode Push Task'),
        default='',
        blank=True,
        null=True)

    objects = models.GeoManager()

    def __unicode__(self):
        ash_event = u'Ash event of [%s] [%s]' % (
            self.volcano, self.event_time)
        return ash_event

    def __init__(self, *args, **kwargs):
        super(Ash, self).__init__(*args, **kwargs)
        self.use_timezone()

    @property
    def reports_queryset(self):
        return self.reports

    @property
    def report_class(self):
        return AshReport

    def use_timezone(self):
        """Use saved timezone information for event_time"""
        # Reformat event_time with timezone
        try:
            tz = pytz.timezone(self.event_time_zone_string)
            self.event_time = self.event_time.astimezone(tz)
        except BaseException:
            pass

    @property
    def event_time_formatted(self):
        return ASH_EVENT_TIME_FORMAT.format(event_time=self.event_time)

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
    def need_generate_hazard(self):
        if self.task_status and not self.task_status == 'None':
            return False
        return True


class AshReport(BaseEventReportModel):
    """Ash Report Model."""

    class Meta(object):
        app_label = 'realtime'
        unique_together = (('ash', 'language'), )

    ash = models.ForeignKey(
        Ash,
        related_name='reports')
    report_map = models.FileField(
        verbose_name=_('Map PDF Report'),
        help_text=_('The map impact report stored as PDF'),
        upload_to='reports/ash/pdf'
    )

    @property
    def event(self):
        return self.ash

    @event.setter
    def event(self, value):
        self.ash = value

    @property
    def canonical_report_pdf(self):
        return self.report_map

    @property
    def canonical_report_filename(self):
        return self.report_map_filename

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
