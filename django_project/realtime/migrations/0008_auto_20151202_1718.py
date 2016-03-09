# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0007_auto_20151118_1117'),
    ]

    operations = [
        migrations.CreateModel(
            name='Boundary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upstream_id', models.CharField(help_text=b'ID used by upstream data source to identify boundaries', unique=True, max_length=64, verbose_name=b'Upstream ID')),
                ('geometry', django.contrib.gis.db.models.fields.PolygonField(help_text=b'Geometry of the boundary', srid=4326, verbose_name=b'Geometry of the boundary')),
            ],
            options={
                'verbose_name_plural': 'Boundaries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BoundaryAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(help_text=b'Alternate or human readable name for boundary level', max_length=64, verbose_name=b'Alias of Boundary Level')),
                ('osm_level', models.IntegerField(help_text=b'OSM Equivalent of boundary level', verbose_name=b'OSM Boundary Level')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Flood',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_id', models.CharField(help_text=b'The id of the event, which represents time and interval', unique=True, max_length=20, verbose_name=b'The id of the event')),
                ('time', models.DateTimeField(help_text=b'The time the flood reported.', verbose_name=b'Date and Time')),
                ('interval', models.IntegerField(default=0, help_text=b'The interval of aggregated report in hours', verbose_name=b'Report interval')),
                ('source', models.CharField(help_text=b'The source of hazard data', max_length=255, verbose_name=b'Flood Data Source')),
                ('region', models.CharField(help_text=b'The region of hazard data', max_length=255, verbose_name=b'The Region id for source')),
                ('impact_layer', models.FileField(help_text=b'Zipped file of Impact Layer related files', upload_to=b'reports/flood/zip', verbose_name=b'Impact Layer', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FloodEventBoundary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('impact_data', models.IntegerField(help_text=b'Impact data in the given boundary', verbose_name=b'Impact Data')),
                ('boundary', models.ForeignKey(verbose_name=b'Boundary', to_field=b'upstream_id', to='realtime.Boundary', help_text=b'The linked boundary of the flood events')),
                ('flood', models.ForeignKey(verbose_name=b'Flood Event', to_field=b'event_id', to='realtime.Flood', help_text=b'The flood event of the linked boundary')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FloodReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(default=b'id', help_text=b'The language ID of the report', max_length=4, verbose_name=b'Language ID')),
                ('impact_report', models.FileField(help_text=b'Impact Report file in PDF', upload_to=b'reports/flood/pdf', verbose_name=b'Impact Report', blank=True)),
                ('impact_map', models.FileField(help_text=b'Impact Map file in PDF', upload_to=b'reports/flood/pdf', verbose_name=b'Impact Map', blank=True)),
                ('flood', models.ForeignKey(related_name='reports', to='realtime.Flood')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='floodreport',
            unique_together=set([('flood', 'language')]),
        ),
        migrations.AlterUniqueTogether(
            name='floodeventboundary',
            unique_together=set([('flood', 'boundary')]),
        ),
        migrations.AddField(
            model_name='flood',
            name='flooded_boundaries',
            field=models.ManyToManyField(help_text=b'The linked boundaries flooded by this event', to='realtime.Boundary', verbose_name=b'Flooded Boundaries', through='realtime.FloodEventBoundary'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='boundary',
            name='boundary_alias',
            field=models.ForeignKey(to='realtime.BoundaryAlias'),
            preserve_default=True,
        ),
    ]
