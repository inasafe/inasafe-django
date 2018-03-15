# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0047_auto_20180315_2101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='earthquakemmicontour',
            name='geometry',
            field=django.contrib.gis.db.models.fields.LineStringField(help_text='Geometry of the MMI contour', srid=4326, verbose_name='Geometry of the MMI contour', dim=3),
        ),
    ]
