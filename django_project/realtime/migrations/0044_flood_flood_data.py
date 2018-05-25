# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0043_auto_20180227_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='flood',
            name='flood_data',
            field=models.TextField(help_text='The content of flood data in json format.', null=True, verbose_name='Flood Data Contents', blank=True),
        ),
    ]
