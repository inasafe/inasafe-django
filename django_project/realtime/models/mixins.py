# coding=utf-8
import json
import logging
import os

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from realtime.app_settings import LOGGER_NAME
from realtime.models.impact import Impact

LOGGER = logging.getLogger(LOGGER_NAME)


class MultiLanguageMixin(object):
    """Generic mixins for hazard event to handle language changes."""

    def __init__(self, *args, **kwargs):
        super(MultiLanguageMixin, self).__init__(*args, **kwargs)
        self._inspected_language = 'en'

    @property
    def inspected_language(self):
        """Language to use when referencing impacts and reports."""
        try:
            return self._inspected_language
        except AttributeError:
            self._inspected_language = 'en'

        return self._inspected_language

    @inspected_language.setter
    def inspected_language(self, value):
        """Set anguage to use when referencing impacts and reports."""

        # Clear impact object and report object cache
        if not self._inspected_language == value:
            self.change_language_hook()
        self._inspected_language = value

    def change_language_hook(self):
        """Do stuff necessary after changing language.

        This meant to be overridden
        """
        raise NotImplementedError(
            'Please handle what happens when changing language.')

    def refresh_from_db(self, using=None, fields=None, **kwargs):
        try:
            lang = self.inspected_language
            super(MultiLanguageMixin, self).refresh_from_db(
                using=using, fields=fields, **kwargs)
            self.inspected_language = lang
        except AttributeError as e:
            LOGGER.warning(e)
            pass


class ImpactMixin(MultiLanguageMixin, models.Model):
    """Generic mixin for hazard to handle multiple impact analysis."""

    class Meta:
        abstract = True

    impacts = GenericRelation(Impact)

    def __init__(self, *args, **kwargs):
        super(ImpactMixin, self).__init__(*args, **kwargs)

        if not hasattr(self, 'impacts'):
            raise AttributeError(
                'Please define GenericRelation impacts')

        self._impact_object = None
        self._analysis_flag = True

    def change_language_hook(self):
        self._impact_object = None

    @property
    def analysis_flag(self):
        return self._analysis_flag

    @analysis_flag.setter
    def analysis_flag(self, value):
        self._analysis_flag = value

    @property
    def has_impacts(self):
        """Check if event has already process an impacts."""
        return bool(self.impact_object)

    @property
    def impact_object(self):
        """Returned impact object for a given inspected language."""
        # Cache object
        if self._impact_object:
            return self._impact_object

        queryset = self.impacts.filter(language=self.inspected_language)
        if queryset:
            self._impact_object = queryset.first()
        else:
            impact = Impact(
                content_object=self, language=self.inspected_language)
            impact.save()
            self._impact_object = impact
        return self._impact_object

    @property
    def analysis_task_id(self):
        """Celery task id of analysis"""
        return self.impact_object.analysis_task_id

    @analysis_task_id.setter
    def analysis_task_id(self, value):
        impact = self.impact_object
        impact.analysis_task_id = value
        impact.save()

    @property
    def analysis_task_status(self):
        """Celery task status of analysis"""
        return self.impact_object.analysis_task_status

    @analysis_task_status.setter
    def analysis_task_status(self, value):
        impact = self.impact_object
        impact.analysis_task_status = value
        impact.save()

    @property
    def analysis_task_result(self):
        """Celery task result of analysis"""
        return self.impact_object.analysis_task_result

    @analysis_task_result.setter
    def analysis_task_result(self, value):
        impact = self.impact_object
        impact.analysis_task_result = value
        impact.save()

    @property
    def impact_file_path(self):
        """Return impact file path given language processed."""
        return self.impact_object.impact_file_path

    @impact_file_path.setter
    def impact_file_path(self, value):
        """Set impact file path given language processed."""
        impact = self.impact_object
        impact.impact_file_path = value
        impact.save()

    @property
    def impact_layer_exists(self):
        """Return bool to indicate existences of impact layers"""
        impact_file_path = self.impact_file_path
        if impact_file_path:
            return os.path.exists(impact_file_path)
        return False

    @property
    def need_run_analysis(self):
        if (self.analysis_task_status and
                not self.analysis_task_status == 'None'):
            return False
        return True

    @property
    def analysis_result(self):
        """Return dict of analysis result."""
        try:
            return json.loads(self.analysis_task_result)
        except (TypeError, ValueError):
            return {}

    def rerun_analysis(self):
        """Rerun Analysis"""
        # Reset analysis state
        self.impacts.all().delete()
        self.save()


class ReportMixin(MultiLanguageMixin, models.Model):
    """Generic mixin for hazard to handle multiple impact analysis report."""

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(ReportMixin, self).__init__(*args, **kwargs)
        self._report_object = None

    def change_language_hook(self):
        self._report_object = None

    @property
    def reports_queryset(self):
        """Get reference to Report model queryset.

        :rtype: models.Manager
        """
        raise NotImplementedError(
            'Please provide references to Report Model queryset')

    @property
    def report_class(self):
        """Get reference to Report model class.

        :rtype: realtime.models.report.BaseEventReportModel | models.Model
        """
        raise NotImplementedError(
            'Please provide references to Report Model class')

    @property
    def canonical_report_pdf(self):
        """Get reference to canonical Report PDF Field.

        :rtype: models.FileField
        """
        return self.report_object.canonical_report_pdf

    @property
    def canonical_report_filename(self):
        """Get reference to canonical Report PDF Filename.

        :rtype: basestring
        """
        return self.report_object.canonical_report_filename

    @property
    def has_reports(self):
        """Check if event has report or not."""
        if self.report_object:
            # Check if report pdf exists
            return bool(self.canonical_report_pdf)
        return False

    @property
    def report_object(self):
        """Returned report object for a given inspected language.

        :rtype: realtime.models.report.BaseEventReportModel | models.Model
        """
        # Cache object
        if self._report_object:
            return self._report_object

        queryset = self.reports_queryset.filter(
            language=self.inspected_language)
        if queryset:
            self._report_object = queryset.first()
        else:
            report = self.report_class()
            report.event = self
            report.language = self.inspected_language
            report.save()
            self._report_object = report
        return self._report_object

    @property
    def report_task_id(self):
        """Celery task id of report"""
        return self.report_object.report_task_id

    @report_task_id.setter
    def report_task_id(self, value):
        report = self.report_object
        report.report_task_id = value
        report.save()

    @property
    def report_task_status(self):
        """Celery task status of report"""
        return self.report_object.report_task_status

    @report_task_status.setter
    def report_task_status(self, value):
        report = self.report_object
        report.report_task_status = value
        report.save()

    @property
    def report_task_result(self):
        """Celery task result of report"""
        return self.report_object.report_task_result

    @report_task_result.setter
    def report_task_result(self, value):
        report = self.report_object
        report.report_task_result = value
        report.save()

    @property
    def need_generate_reports(self):
        if (self.report_task_status and
                not self.report_task_status == 'None'):
            return False
        return True

    @property
    def report_result(self):
        """Return dict of report result."""
        try:
            return json.loads(self.report_task_result)
        except (TypeError, ValueError):
            return {}

    def rerun_report_generation(self):
        """Rerun Report Generations"""

        # Delete existing reports
        reports = self.reports_queryset.all()

        for r in reports:
            r.delete()

        self.save()


class BaseEventModel(ImpactMixin, ReportMixin, models.Model):
    """"""

    class Meta:
        abstract = True

    hazard_path = models.CharField(
        verbose_name=_('Hazard Layer path'),
        help_text=_('Location of hazard layer'),
        max_length=255,
        default=None,
        null=True,
        blank=True)
    inasafe_version = models.CharField(
        verbose_name=_('InaSAFE version'),
        help_text=_('InaSAFE version being used'),
        max_length=10,
        default=None,
        null=True,
        blank=True)

    @property
    def event_id_formatted(self):
        """Return a formatted event id of hazard."""
        raise NotImplementedError(
            'Please implement formatted event id on inherited models.')

    @property
    def hazard_layer_exists(self):
        """Return bool to indicate existences of hazard layer"""
        if self.hazard_path:
            return os.path.exists(self.hazard_path)
        return False

    def change_language_hook(self):
        ImpactMixin.change_language_hook(self)
        ReportMixin.change_language_hook(self)
