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
    report_pdf = models.FileField(
        verbose_name='PDF Report',
        help_text='The impact report stored as PDF',
        upload_to='reports/pdf',
        null=True)
    report_image = models.ImageField(
        verbose_name='Image Report',
        help_text='The impact report stored as PNG File',
        upload_to='reports/png',
        null=True)
    report_thumbnail = models.ImageField(
        verbose_name='Image Report Thumbnail',
        help_text='The thumbnail of the report stored as PNG File',
        upload_to='reports/thumbnail',
        null=True)

    objects = models.GeoManager()
