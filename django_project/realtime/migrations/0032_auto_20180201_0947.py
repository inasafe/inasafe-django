# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0031_auto_20171220_1224'),
    ]

    operations = [
        migrations.AddField(
            model_name='ash',
            name='forecast_duration',
            field=models.IntegerField(default=1, verbose_name='Duration of forecast for Ash Hazard'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ash',
            name='eruption_height',
            field=models.IntegerField(default=0, verbose_name='Eruption height in metres. Calculated from the vent height'),
            preserve_default=True,
        ),
    ]
