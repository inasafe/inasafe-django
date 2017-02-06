# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0023_auto_20161022_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ash',
            name='hazard_file',
            field=models.FileField(help_text=b'Hazard file formatted as GeoTIFF (*.tif) in EPSG:4326.', upload_to=b'ash/hazard_file/%Y/%m/%d', verbose_name=b'Hazard File'),
            preserve_default=True,
        ),
    ]
