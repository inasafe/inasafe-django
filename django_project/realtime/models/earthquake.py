# coding=utf-8
"""Model class for earthquake realtime."""

from django.contrib.gis.db import models


class Earthquake(models.Model):
    """Earthquake model."""
    class Meta:
        """Meta class."""
        app_label = 'realtime'

    shake_id = models.CharField(
        verbose_name='The Shake ID',
        help_text='The Shake ID, which represents the time of the event.',
        max_length='14',
        blank=False,
        unique=True)
    shake_grid = models.FileField(
        verbose_name='Shake Grid XML File',
        help_text='The Shake Grid to process',
        upload_to='earthquake/grid',
        blank=True,
        null=True)
    magnitude = models.FloatField(
        verbose_name='The magnitude',
        help_text='The magnitude of the event.')
    time = models.DateTimeField(
        verbose_name='Date and Time',
        help_text='The time the shake happened.',
        blank=False)
    depth = models.FloatField(
        verbose_name='The depth',
        help_text='The depth of the event in km unit.')
    location = models.PointField(
        verbose_name='Location',
        help_text='The location of the shake event in longitude and latitude.',
        srid=4326,
        max_length=255,
        null=False,
        blank=False)
    location_description = models.CharField(
        verbose_name='Location Description',
        help_text='The description of the location e.g "Bali".',
        max_length=255)

    objects = models.GeoManager()

    def __unicode__(self):
        shake_string = u'Shake event [%s]' % self.shake_id
        if self.location_description.strip():
            shake_string += u' in %s' % self.location_description
        return shake_string

    def delete(self, using=None):
        # delete all report
        if self.shake_grid:
            self.shake_grid.delete()
        for report in self.reports.all():
            report.delete(using=using)
        super(Earthquake, self).delete(using=using)


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
        verbose_name='Language ID',
        help_text='The language ID of the report',
        max_length=4,
        default='id'
    )
    report_pdf = models.FileField(
        verbose_name='PDF Report',
        help_text='The impact report stored as PDF',
        upload_to='reports/earthquake/pdf',
        null=True)
    report_image = models.ImageField(
        verbose_name='Image Report',
        help_text='The impact report stored as PNG File',
        upload_to='reports/earthquake/png',
        null=True)
    report_thumbnail = models.ImageField(
        verbose_name='Image Report Thumbnail',
        help_text='The thumbnail of the report stored as PNG File',
        upload_to='reports/earthquake/thumbnail',
        null=True)

    def delete(self, using=None):
        # delete stored files
        self.report_pdf.delete()
        self.report_image.delete()
        self.report_thumbnail.delete()
        super(EarthquakeReport, self).delete(using=using)
