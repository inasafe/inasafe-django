# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0045_auto_20180301_0235'),
    ]

    operations = [
        migrations.CreateModel(
            name='EarthquakeMMIContour',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.MultiPolygonField(help_text='Geometry of the MMI contour', srid=4326, verbose_name='Geometry of the MMI contour')),
                ('mmi', models.FloatField(help_text='MMI value', verbose_name='MMI value')),
                ('properties', models.TextField(help_text='JSON representations of feature properties.', verbose_name='JSON representations of feature properties.')),
                ('earthquake', models.ForeignKey(related_name='contours', to='realtime.Earthquake')),
            ],
        ),
    ]
