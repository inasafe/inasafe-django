# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='earthquake',
            name='report_image',
            field=models.ImageField(help_text=b'The impact report stored as PNG File', upload_to=b'reports/png', null=True, verbose_name=b'Image Report'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='earthquake',
            name='report_pdf',
            field=models.FileField(help_text=b'The impact report stored as PDF', upload_to=b'reports/pdf', null=True, verbose_name=b'PDF Report'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='earthquake',
            name='report_thumbnail',
            field=models.ImageField(help_text=b'The thumbnail of the report stored as PNG File', upload_to=b'reports/thumbnail', null=True, verbose_name=b'Image Report Thumbnail'),
            preserve_default=True,
        ),
    ]
