# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0012_earthquake_shake_grid'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImpactEventBoundary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.MultiPolygonField(help_text=b'Geometry of the boundary of impact', srid=4326, verbose_name=b'Geometry of the boundary of impact')),
                ('hazard_class', models.IntegerField(help_text=b'Hazard class in the given boundary', null=True, verbose_name=b'Hazard Class', blank=True)),
                ('population_affected', models.IntegerField(help_text=b'The affected population in a given flood boundary', null=True, verbose_name=b'Population Affected', blank=True)),
                ('flood', models.ForeignKey(related_name='impact_event', verbose_name=b'Flood Event', to_field=b'event_id', to='realtime.Flood', help_text=b'The flood event of the linked boundary')),
                ('parent_boundary', models.ForeignKey(related_name='impact_event', verbose_name=b'Boundary', to='realtime.Boundary', help_text=b'The linked parent boundary of the impact')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameField(
            model_name='floodeventboundary',
            old_name='impact_data',
            new_name='hazard_data',
        ),
        migrations.AddField(
            model_name='flood',
            name='impact_layer',
            field=models.FileField(help_text=b'Zipped file of Impact Layer related files', upload_to=b'reports/flood/zip', verbose_name=b'Impact Layer', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='earthquake',
            name='shake_grid',
            field=models.FileField(help_text=b'The Shake Grid to process', upload_to=b'earthquake/grid', null=True, verbose_name=b'Shake Grid XML File', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='earthquakereport',
            name='report_image',
            field=models.ImageField(help_text=b'The impact report stored as PNG File', upload_to=b'reports/earthquake/png', null=True, verbose_name=b'Image Report'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='earthquakereport',
            name='report_pdf',
            field=models.FileField(help_text=b'The impact report stored as PDF', upload_to=b'reports/earthquake/pdf', null=True, verbose_name=b'PDF Report'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='earthquakereport',
            name='report_thumbnail',
            field=models.ImageField(help_text=b'The thumbnail of the report stored as PNG File', upload_to=b'reports/earthquake/thumbnail', null=True, verbose_name=b'Image Report Thumbnail'),
            preserve_default=True,
        ),
    ]
