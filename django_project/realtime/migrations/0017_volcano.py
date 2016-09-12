# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0016_update_rest_groups'),
    ]

    operations = [
        migrations.CreateModel(
            name='Volcano',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('volcano_name', models.CharField(help_text=b'The name of the volcano', max_length=50, verbose_name=b'The Volcano Name')),
                ('location', django.contrib.gis.db.models.fields.PointField(help_text=b'The location of the shake event in longitude and latitude.', srid=4326, verbose_name=b'Location')),
                ('elevation', models.IntegerField(default=0, help_text=b'The elevation of the volcano in meters', verbose_name=b'Volcano Elevation')),
                ('region', models.CharField(help_text=b'The region where the volcano located', max_length=50, verbose_name=b'The region main name', blank=True)),
                ('subregion', models.CharField(help_text=b'The sub region where the volcano located', max_length=50, verbose_name=b'The sub region main name', blank=True)),
                ('morphology', models.CharField(help_text=b'Morphology of the volcano', max_length=50, verbose_name=b'Morphology', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
