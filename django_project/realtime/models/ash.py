# coding=utf-8
"""Model class for ash realtime."""

from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

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
    eruption_height = models.IntegerField(
        verbose_name=_('Eruption height in metres'),
        blank=False,
        default=0)
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

    objects = models.GeoManager()

    def __unicode__(self):
        ash_event = u'Ash event of [%s] [%s]' % (
            self.volcano, self.event_time)
        return ash_event

    def delete(self, using=None):
        # delete all report
        if self.hazard_file:
            self.hazard_file.delete()
        if self.impact_files:
            self.impact_files.delete()
        return super(Ash, self).delete(using=using)


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

    def delete(self, using=None):
        self.report_map.delete()
        return super(AshReport, self).delete(using=using)
