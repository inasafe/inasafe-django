# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0009_update_rest_groups'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flood',
            name='impact_layer',
        ),
        migrations.AddField(
            model_name='boundary',
            name='name',
            field=models.CharField(help_text=b'Name entitled to this particular boundary', max_length=64, null=True, verbose_name=b'The name of the boundary', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='boundary',
            name='parent',
            field=models.ForeignKey(blank=True, to='realtime.Boundary', help_text=b'The boundary parent of this particular boundary, if any. This should also be a boundary.', null=True, verbose_name=b'Parent boundary'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='boundaryalias',
            name='parent',
            field=models.ForeignKey(blank=True, to='realtime.BoundaryAlias', help_text=b'The parent of this boundary alias, it should also be a boundary alias', null=True, verbose_name=b'Parent boundary alias'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flood',
            name='hazard_layer',
            field=models.FileField(help_text=b'Zipped file of Hazard Layer related files', upload_to=b'reports/flood/zip', verbose_name=b'Hazard Layer', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='boundary',
            name='boundary_alias',
            field=models.ForeignKey(blank=True, to='realtime.BoundaryAlias', help_text=b'The alias of boundary level of this boundary', null=True, verbose_name=b'Boundary level alias'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='boundary',
            name='geometry',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(help_text=b'Geometry of the boundary', srid=4326, verbose_name=b'Geometry of the boundary'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='floodeventboundary',
            name='impact_data',
            field=models.IntegerField(help_text=b'Impact data in the given boundary', null=True, verbose_name=b'Impact Data', blank=True),
            preserve_default=True,
        ),
    ]
