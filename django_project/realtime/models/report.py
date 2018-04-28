# coding=utf-8

from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _


class BaseEventReportModel(models.Model):
    """Base model for event report."""

    class Meta:
        abstract = True

    language = models.CharField(
        verbose_name=_('Language ID'),
        help_text=_('The language ID of the report'),
        max_length=4,
        default='id')
    report_task_id = models.CharField(
        verbose_name=_('Report celery task id'),
        help_text=_('Task id for creating analysis report.'),
        max_length=255,
        default='',
        blank=True)
    report_task_status = models.CharField(
        verbose_name=_('Report celery task status'),
        help_text=_('Task status for creating analysis report.'),
        max_length=30,
        default='None',
        blank=True)
    report_task_result = models.TextField(
        verbose_name=_('Report celery task result'),
        help_text=_('Task result of report generation'),
        default='',
        blank=True,
        null=True)

    @property
    def event(self):
        """Get reference to related event."""
        raise NotImplementedError(
            'Please provide references to related event.')

    @property
    def canonical_report_pdf(self):
        """Get reference to canonical Report PDF Field."""
        raise NotImplementedError(
            'Please provide references to canonical Report PDF Field.')

    @property
    def canonical_report_filename(self):
        """Get reference to canonical Report PDF Filename."""
        raise NotImplementedError(
            'Please provide references to canonical Report PDF Filename.')

