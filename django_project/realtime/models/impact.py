# coding=utf-8
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class Impact(models.Model):
    """InaSAFE Impact Analysis model."""

    class Meta:
        """Meta class."""
        app_label = 'realtime'

    # ContentType required fields
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    impact_file_path = models.CharField(
        verbose_name=_('Impact File path'),
        help_text=_('Location of impact file.'),
        max_length=255,
        default=None,
        blank=True,
        null=True)
    analysis_task_id = models.CharField(
        verbose_name=_('Analysis celery task id'),
        help_text=_('Task id for running analysis'),
        max_length=255,
        default='',
        blank=True)
    analysis_task_status = models.CharField(
        verbose_name=_('Analysis celery task status'),
        help_text=_('Task status for running analysis'),
        max_length=30,
        default='None',
        blank=True)
    analysis_task_result = models.TextField(
        verbose_name=_('Analysis celery task result'),
        help_text=_('Task result of analysis run'),
        default='',
        blank=True,
        null=True)
    language = models.CharField(
        verbose_name=_('Language ID'),
        help_text=_('The language ID of the report'),
        max_length=4,
        default='id')

    def content_object_url(self):
        change_url_name = 'realtime_admin:{app_label}_{content_type}_change'
        change_url_name = change_url_name.format(
            app_label=self.content_object._meta.app_label,
            content_type=self.content_type.name)
        return reverse(change_url_name, args=(self.content_object.id, ))

    def __unicode__(self):
        impact_string = u'Impact analysis [{0}] [{1}]'.format(
            self.content_object,
            self.language)
        return impact_string
