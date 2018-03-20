# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0046_earthquakemmicontour'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flood',
            name='source_type',
        ),
        migrations.AlterField(
            model_name='earthquakemmicontour',
            name='geometry',
            field=django.contrib.gis.db.models.fields.LineStringField(help_text='Geometry of the MMI contour', srid=4326, verbose_name='Geometry of the MMI contour'),
        ),
        migrations.AlterField(
            model_name='flood',
            name='source',
            field=models.CharField(default=None, max_length=255, blank=True, help_text='The source of hazard data', null=True, verbose_name='Flood Data Source'),
        ),
    ]
