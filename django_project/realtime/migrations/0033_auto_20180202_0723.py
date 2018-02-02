# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0032_auto_20180201_0947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ash',
            name='forecast_duration',
            field=models.IntegerField(default=1, verbose_name='Duration of forecast for Ash Hazard in days'),
            preserve_default=True,
        ),
    ]
