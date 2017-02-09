# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0025_auto_20170206_2046'),
    ]

    operations = [
        migrations.AddField(
            model_name='ash',
            name='impact_files',
            field=models.FileField(help_text=b'Impact files processed zipped', upload_to=b'ash/impact_files/%Y/%m/%d', null=True, verbose_name=b'Impact Files', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='earthquake',
            name='mmi_output',
            field=models.FileField(help_text=b'MMI related file, layers, and data, zipped.', upload_to=b'earthquake/mmi_output', null=True, verbose_name=b'MMI related file zipped', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ash',
            name='eruption_height',
            field=models.IntegerField(default=0, verbose_name=b'Eruption height in metres'),
            preserve_default=True,
        ),
    ]
