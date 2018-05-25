# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0052_auto_20180425_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='volcano',
            name='timezone',
            field=models.CharField(help_text='The TimeZone where the volcano located', max_length=50, verbose_name='TimeZone', blank=True),
        ),
    ]
