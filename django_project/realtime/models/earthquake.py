# coding=utf-8
"""Model class for earthquake realtime."""
import json
import os

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from realtime.app_settings import EARTHQUAKE_EVENT_REPORT_FORMAT, \
    EARTHQUAKE_EVENT_ID_FORMAT
from realtime.models.impact import Impact
from realtime.utils import split_layer_ext


class Earthquake(models.Model):
    """Earthquake model."""

    INITIAL_SOURCE_TYPE = 'initial'
    CORRECTED_SOURCE_TYPE = 'corrected'

    class Meta:
        """Meta class."""
        app_label = 'realtime'
        unique_together = (('shake_id', 'source_type'), )
        ordering = ['-time', '-shake_id', '-source_type']

    # Shake ID of corrected shakemaps can go as far as:
    # 20180316015829_52_-6050_142170_20180316015829
    shake_id = models.CharField(
        verbose_name=_('The Shake ID'),
        help_text=_('The Shake ID, which represents the time of the event.'),
        max_length=50,
        blank=False)
    shake_grid = models.FileField(
        verbose_name=_('Shake Grid XML File'),
        help_text=_('The Shake Grid to process'),
        upload_to='earthquake/grid',
        blank=True,
        null=True)
    shake_grid_xml = models.TextField(
        verbose_name=_('Shake Grid XML File Contents'),
        help_text=_('The content of shake grid file'),
        blank=True,
        null=True)
    mmi_output = models.FileField(
        verbose_name=_('MMI related file zipped'),
        help_text=_('MMI related file, layers, and data, zipped.'),
        upload_to='earthquake/mmi_output',
        blank=True,
        null=True)
    mmi_output_path = models.CharField(
        verbose_name=_('MMI related file path'),
        help_text=_('MMI related file path location'),
        max_length=255,
        blank=True,
        null=True,
        default=None)
    magnitude = models.FloatField(
        verbose_name=_('The magnitude'),
        help_text=_('The magnitude of the event.'))
    time = models.DateTimeField(
        verbose_name=_('Date and Time'),
        help_text=_('The time the shake happened.'),
        blank=False)
    generated_time = models.DateTimeField(
        verbose_name=_('Report Generated Date and Time'),
        help_text=_('The time the shake report generated.'),
        blank=True,
        null=True,
        default=None)
    depth = models.FloatField(
        verbose_name=_('The depth'),
        help_text=_('The depth of the event in km unit.'))
    location = models.PointField(
        verbose_name=_('Location'),
        help_text=_(
            'The location of the shake event in longitude and latitude.'),
        srid=4326,
        max_length=255,
        null=False,
        blank=False)
    location_description = models.CharField(
        verbose_name=_('Location Description'),
        help_text=_('The description of the location e.g "Bali".'),
        max_length=255)
    felt = models.BooleanField(
        verbose_name=_('Felt Earthquake'),
        help_text=_("Set to True if this particular event showed up as felt "
                    "Earthquake in BMKG's List"),
        default=False)
    source_type = models.CharField(
        verbose_name=_('Source Type'),
        help_text=_('Source type of shake grid'),
        max_length=30,
        default='initial')
    hazard_path = models.CharField(
        verbose_name=_('Hazard Layer path'),
        help_text=_('Location of hazard layer'),
        max_length=255,
        default=None,
        null=True,
        blank=True)
    has_corrected = models.BooleanField(
        verbose_name=_(
            'Cache flag to tell that this shakemap has a corrected version.'),
        default=False)
    mmi_layer_saved = models.BooleanField(
        verbose_name=_(
            'Cache flag to tell that this shakemap already saved its '
            'contours.'),
        default=False)
    impacts = GenericRelation(Impact, related_query_name='earthquake')
    inasafe_version = models.CharField(
        verbose_name=_('InaSAFE version'),
        help_text=_('InaSAFE version being used'),
        max_length=10,
        default=None,
        null=True,
        blank=True)

    objects = models.GeoManager()

    def __init__(self, *args, **kwargs):
        super(Earthquake, self).__init__(*args, **kwargs)
        self._impact_object = None
        self._report_object = None
        self._inspected_language = 'en'

    def __unicode__(self):
        shake_string = u'Shake event [{0}]'.format(self.event_id_formatted)
        if self.location_description.strip():
            shake_string += u' in {0}'.format(self.location_description)
        return shake_string

    def delete(self, using=None):
        # delete all report
        if self.shake_grid:
            self.shake_grid.delete()
        if self.mmi_output:
            self.mmi_output.delete()
        for report in self.reports.all():
            report.delete(using=using)
        super(Earthquake, self).delete(using=using)

    def mark_shakemaps_has_corrected(self):
        """Mark cache flag of has_corrected.
        This is to tell that this shakemaps have shakemaps corrected.
        """
        # Only for initial shakemaps
        if self.source_type == self.INITIAL_SOURCE_TYPE:
            has_corrected = bool(self.corrected_shakemaps)
            Earthquake.objects.filter(id=self.id).update(
                has_corrected=has_corrected)

    def mark_shakemaps_has_contours(self):
        """Mark cache flag of mmi_layer_saved.
        This is to tell that this shakemaps have contours saved in database.
        """
        mmi_layer_saved = bool(self.contours.all().count() > 0)
        Earthquake.objects.filter(id=self.id).update(
            mmi_layer_saved=mmi_layer_saved)

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
        if self._impact_object and self._report_object:
            if not self._inspected_language == value:
                self._impact_object = None
                self._report_object = None
        self._inspected_language = value

    def refresh_from_db(self, using=None, fields=None, **kwargs):
        lang = self.inspected_language
        super(Earthquake, self).refresh_from_db(
            using=using, fields=fields, **kwargs)
        self.inspected_language = lang

    @property
    def hazard_layer_exists(self):
        """Return bool to indicate existences of hazard layer"""
        if self.hazard_path:
            return os.path.exists(self.hazard_path)
        return False

    @property
    def has_reports(self):
        """Check if event has report or not."""
        if self.report_object:
            # Check if report pdf exists
            return bool(self.report_object.report_pdf)
        return False

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
    def report_object(self):
        """Returned report object for a given inspected language."""
        # Cache object
        if self._report_object:
            return self._report_object

        queryset = self.reports.filter(language=self.inspected_language)
        if queryset:
            self._report_object = queryset.first()
        else:
            report = EarthquakeReport.objects.create(
                earthquake=self,
                language=self.inspected_language)
            self._report_object = report
        return self._report_object

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
    def shake_grid_exists(self):
        return bool(self.shake_grid or self.shake_grid_xml)

    @property
    def mmi_layer_exists(self):
        """Return bool to indicate existences of impact layers"""
        if self.impact_file_path:
            return os.path.exists(self.mmi_output_path)
        return False

    @property
    def analysis_zip_path(self):
        """Return analysis zip path for download."""
        dirname = os.path.dirname(self.impact_file_path)
        basename = os.path.basename(self.impact_file_path)
        basename_without_ext = split_layer_ext(basename)[0]
        zip_path = os.path.join(dirname, basename_without_ext + '.zip')
        if os.path.exists(zip_path):
            return zip_path
        return None

    @property
    def shake_grid_download_url(self):
        if self.shake_grid_exists:
            return reverse('realtime:shake_grid', kwargs={
                'shake_id': self.shake_id,
                'source_type': self.source_type
            })
        return None

    @property
    def mmi_layer_download_url(self):
        if self.mmi_layer_saved:
            return reverse('realtime:earthquake_mmi_contours_list', kwargs={
                'shake_id': self.shake_id,
                'source_type': self.source_type
            })
        return None

    @property
    def analysis_zip_download_url(self):
        if self.mmi_layer_exists:
            return reverse('realtime:analysis_zip', kwargs={
                'shake_id': self.shake_id,
                'source_type': self.source_type
            })
        return None

    @property
    def need_run_analysis(self):
        if (self.analysis_task_status and
                not self.analysis_task_status == 'None'):
            return False
        return True

    @property
    def need_generate_reports(self):
        if (self.report_task_status and
                not self.report_task_status == 'None'):
            return False
        return True

    @property
    def analysis_result(self):
        """Return dict of analysis result."""
        try:
            return json.loads(self.analysis_task_result)
        except (TypeError, ValueError):
            return {}

    @property
    def report_result(self):
        """Return dict of report result."""
        try:
            return json.loads(self.report_task_result)
        except (TypeError, ValueError):
            return {}

    @property
    def event_id_formatted(self):
        return EARTHQUAKE_EVENT_ID_FORMAT.format(
            shake_id=self.shake_id,
            source_type=self.source_type
        )

    @property
    def grid_xml_filename(self):
        return '{event_id_formatted}-grid.xml'.format(
            event_id_formatted=self.event_id_formatted)

    @property
    def mmi_layer_filename(self):
        return '{event_id_formatted}-mmi.geojson'.format(
            event_id_formatted=self.event_id_formatted)

    def shakemaps_matching_queryset(self, source_type):
        """Return a proper queryset match to retrieve matching shakemaps."""
        # return a combination of querysets

        # Find exact info match
        exact_combination_match = Earthquake.objects.filter(
            time=self.time,
            location=self.location,
            magnitude=self.magnitude,
            source_type=source_type)

        if exact_combination_match:
            return exact_combination_match

        # Find exact time match
        exact_time_match = Earthquake.objects.filter(
            time=self.time,
            source_type=source_type)

        return exact_time_match

        # The following section were commented out until we have a proper
        # algorithm

        # # find a range of shakemaps in a given range, sorted with:
        # # - least time diff
        # # - least magnitude diff
        # # - least location diff
        #
        # # it is difficult to have an absolute time diff using sql alone, so
        # # will try to find the match using date range
        # # Use a maximum of an hour difference
        # delta_time = datetime.timedelta(minutes=30)
        # end_time = self.time + delta_time
        # start_time = self.time - delta_time
        #
        # # A range of 1 MMI
        # magnitude_delta = 1
        # # A range of 10 km
        # distance_delta = 10000
        #
        # within_time_range_with_location_match = Earthquake.objects\
        #     .filter(
        #         time__range=[start_time, end_time],
        #         source_type=self.CORRECTED_SOURCE_TYPE)\
        #     .annotate(
        #         # add magnitude diff
        #         magnitude_diff=Func(
        #             F('magnitude') - self.magnitude,
        #             function='ABS'))\
        #     .distance(self.location)\
        #     .filter(
        #         magnitude_diff__lte=magnitude_delta,
        #         distance__lte=distance_delta
        #     )\
        #     .order_by('-time', 'distance', 'magnitude_diff')
        #
        # return within_time_range_with_location_match

    def corrected_shakemaps_queryset(self):
        """Find a corrected shakemaps matching this one."""
        return self.shakemaps_matching_queryset(self.CORRECTED_SOURCE_TYPE)

    def initial_shakemaps_queryset(self):
        """Find initial shakemaps matching this one."""
        return self.shakemaps_matching_queryset(self.INITIAL_SOURCE_TYPE)

    @property
    def corrected_shakemaps(self):
        """Return the corrected version of the shakemaps if any."""
        if self.source_type == self.CORRECTED_SOURCE_TYPE:
            # Not Applicable
            return None

        # Return only the latest one
        return self.corrected_shakemaps_queryset().order_by(
            '-shake_id').first()

    @property
    def initial_shakemaps(self):
        """Return the initial version of the shakemaps if any."""
        if self.source_type == self.INITIAL_SOURCE_TYPE:
            # Not Applicable
            return None

        # There should be only one
        return self.initial_shakemaps_queryset().first()

    def rerun_report_generation(self):
        """Rerun Report Generations"""

        # Delete existing reports
        reports = self.reports.all()

        for r in reports:
            r.delete()

        self.report_task_result = ''
        self.report_task_status = ''
        self.save()

    def rerun_analysis(self):
        """Rerurn Analysis"""

        # Delete existing reports
        reports = self.reports.all()

        for r in reports:
            r.delete()

        self.report_task_result = ''
        self.report_task_status = ''

        # Reset analysis state
        self.impacts.all().delete()
        self.analysis_task_result = ''
        self.analysis_task_status = ''
        self.save()


class EarthquakeMMIContour(models.Model):
    """Earthquake MMI Contour Model."""

    class Meta:
        """Meta class."""
        app_label = 'realtime'

    earthquake = models.ForeignKey(
        Earthquake,
        related_name='contours')
    geometry = models.LineStringField(
        verbose_name=_('Geometry of the MMI contour'),
        help_text=_('Geometry of the MMI contour'),
        dim=3,
        blank=False)
    mmi = models.FloatField(
        verbose_name=_('MMI value'),
        help_text=_('MMI value'),
        blank=False)
    properties = models.TextField(
        verbose_name=_('JSON representations of feature properties.'),
        help_text=_('JSON representations of feature properties.'),
        blank=False)

    def __unicode__(self):
        description = u'MMI Contour {mmi} of {event_id_formatted}'.format(
            mmi=self.mmi,
            event_id_formatted=self.earthquake.event_id_formatted)
        return description


class EarthquakeReport(models.Model):
    """Earthquake Report Model."""

    class Meta:
        """Meta class."""
        app_label = 'realtime'
        unique_together = (('earthquake', 'language'),)

    earthquake = models.ForeignKey(
        Earthquake,
        related_name='reports')
    language = models.CharField(
        verbose_name=_('Language ID'),
        help_text=_('The language ID of the report'),
        max_length=4,
        default='id'
    )
    report_pdf = models.FileField(
        verbose_name=_('PDF Report'),
        help_text=_('The impact report stored as PDF'),
        upload_to='reports/earthquake/pdf',
        null=True)
    report_image = models.ImageField(
        verbose_name=_('Image Report'),
        help_text=_('The impact report stored as PNG File'),
        upload_to='reports/earthquake/png',
        null=True)
    report_thumbnail = models.ImageField(
        verbose_name=_('Image Report Thumbnail'),
        help_text=_('The thumbnail of the report stored as PNG File'),
        upload_to='reports/earthquake/thumbnail',
        null=True)
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

    def delete(self, using=None):
        # delete stored files
        self.report_pdf.delete()
        self.report_image.delete()
        self.report_thumbnail.delete()
        super(EarthquakeReport, self).delete(using=using)

    def __unicode__(self):
        description = u'Report lang [{lang}] of [{event_id_formatted}]'.format(
            lang=self.language,
            event_id_formatted=self.earthquake.event_id_formatted)
        return description

    @property
    def shake_id(self):
        return self.earthquake.shake_id

    @property
    def source_type(self):
        return self.earthquake.source_type

    @property
    def report_map_filename(self):
        """Return standardized filename for report map."""
        return EARTHQUAKE_EVENT_REPORT_FORMAT.format(
            shake_id=self.earthquake.shake_id,
            source_type=self.earthquake.source_type,
            language=self.language,
            suffix='',
            extension='pdf')

    @property
    def report_image_filename(self):
        """Return standardized filename for report map."""
        return EARTHQUAKE_EVENT_REPORT_FORMAT.format(
            shake_id=self.earthquake.shake_id,
            source_type=self.earthquake.source_type,
            language=self.language,
            suffix='',
            extension='png')

    @property
    def report_thumbnail_filename(self):
        """Return standardized filename for report map."""
        return EARTHQUAKE_EVENT_REPORT_FORMAT.format(
            shake_id=self.earthquake.shake_id,
            source_type=self.earthquake.source_type,
            language=self.language,
            suffix='-thumbnail',
            extension='png')
