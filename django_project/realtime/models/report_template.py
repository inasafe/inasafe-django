# coding=utf-8
"""Model class for Report Template."""
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

__author__ = 'myarjunar'
__project_name__ = 'inasafe-django'
__filename__ = 'report_template'
__date__ = '7/15/16'
__copyright__ = 'myarjuanar@gmail.com'


class ReportTemplate(models.Model):
    """ReportTemplate model."""
    class Meta:
        """Meta class."""
        app_label = 'realtime'
        verbose_name_plural = 'Report Templates'

    timestamp = models.DateTimeField(
        verbose_name=_('Timestamp'),
        help_text=_('The time the template uploaded.'),
        blank=False
    )

    version = models.CharField(
        verbose_name=_('Template version'),
        help_text=_('Version number of the template.'),
        max_length=10,
        default=None,
        null=True,
        blank=True
    )

    notes = models.CharField(
        verbose_name=_('Template Notes'),
        help_text=_('Notes of the report template.'),
        max_length=255,
        default=None,
        blank=True,
        null=True
    )

    language = models.CharField(
        verbose_name=_('Language ID'),
        help_text=_('The language ID of the report'),
        max_length=4,
        default='id'
    )

    hazard = models.CharField(
        verbose_name=_('Hazard Type'),
        help_text=_('The hazard type of the template.'),
        max_length=25,
        default=None,
        blank=False,
        null=False
    )

    template_file = models.TextField(
        verbose_name=_('Template File'),
        help_text=_('Template file formatted as qgis template file (*.qpt).'),
        blank=False
    )

    owner = models.IntegerField(
        verbose_name=_('Owner'),
        help_text=_('The owner/uploader of the template.'),
        default=0
    )
