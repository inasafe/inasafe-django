# coding=utf-8
"""Model class for InaSAFE Role"""
from django.contrib.gis.db import models


class InasafeRole(models.Model):
    """InaSAFE Role for users e.g. InaSAFE developer, trainer, user."""
    class Meta:
        """Meta class."""
        app_label = 'user_map'

    name = models.CharField(
        help_text='How would you define your InaSAFE Role in this project?',
        max_length=100,
        null=False,
        blank=False)
    badge = models.CharField(
        help_text='The path to the badge',
        max_length=200,
        null=False,
        blank=False)
    sort_number = models.IntegerField(
        help_text='Sorting order for role in role list.',
        null=True,
        blank=True)

    def __unicode__(self):
        return self.name
