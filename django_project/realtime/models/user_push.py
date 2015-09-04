# coding=utf-8
"""
Model class for Realtime User related
"""

from datetime import datetime
from django.contrib.gis.db import models
from user_map.models.user import User

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '02/09/15'


class UserPush(models.Model):
    """UserPush models.

    UserPush is used to check Realtime 'healthiness' and 'reliability'.
    It is mainly used to make sure that Realtime is running.
    """

    class Meta:
        app_label = 'realtime'

    # should be tied to a unique user in Realtime REST Group
    user = models.OneToOneField(User)
    last_shakemap_push = models.DateTimeField(
        verbose_name='Last shakemap push',
        help_text='Date and time of last shakemap push made by user',
        default=datetime.utcfromtimestamp(0)
    )
    last_rest_push = models.DateTimeField(
        verbose_name='Last REST push',
        help_text='Date and time of last Earthquake REST post made by user',
        default=datetime.utcfromtimestamp(0)
    )
