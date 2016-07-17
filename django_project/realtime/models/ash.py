# coding=utf-8
"""Model class for earthquake realtime."""

from django.contrib.gis.db import models

__author__ = 'ismailsunni'
__project_name__ = 'inasafe-django'
__filename__ = 'ash'
__date__ = '7/15/16'
__copyright__ = 'imajimatika@gmail.com'


class Ash(models.Model):
    """Earthquake model."""
    class Meta:
        """Meta class."""
        app_label = 'realtime'

    volcano_name = models.CharField(
        verbose_name='The Volcano Name',
        help_text='The name of the volcano',
        max_length='30',
        blank=False)
    location = models.PointField(
        verbose_name='Location',
        help_text='The location of the shake event in longitude and latitude.',
        srid=4326,
        max_length=255,
        null=False,
        blank=False)
    alert_level = models.CharField(
        verbose_name='Alert Level',
        help_text='The alert level of the volcano ash event.',
        max_length='30',
        blank=False
    )
    hazard_file = models.FileField(
        verbose_name='Hazard File',
        help_text='Collection of hazard file in zip.',
        upload_to='ash/hazard_file/%Y/%m/%d',
        blank=False
    )
    eruption_height = models.FloatField(
        verbose_name='Eruption Height',
        help_text='The height of the eruption in meter unit',
    )
    event_time = models.DateTimeField(
        verbose_name='Event Date and Time',
        help_text='The time the ash happened.',
        blank=False)
    region = models.CharField(
        verbose_name='Region',
        help_text='The region where the ash happened, e.g. Jawa Timur.',
        max_length='30',
        blank=False
    )

    objects = models.GeoManager()

    def __unicode__(self):
        ash_event = u'Ash event of [%s]' % self.volcano_name
        if self.region:
            ash_event += u' in %s' % self.region
        return ash_event

    def delete(self, using=None):
        # delete all report
        if self.hazard_file:
            self.hazard_file.delete()
        super(Ash, self).delete(using=using)
