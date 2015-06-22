# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EarthquakeReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('report_pdf', models.FileField(help_text=b'The impact report stored as PDF', upload_to=b'reports/pdf', null=True, verbose_name=b'PDF Report')),
                ('report_image', models.ImageField(help_text=b'The impact report stored as PNG File', upload_to=b'reports/png', null=True, verbose_name=b'Image Report')),
                ('report_thumbnail', models.ImageField(help_text=b'The thumbnail of the report stored as PNG File', upload_to=b'reports/thumbnail', null=True, verbose_name=b'Image Report Thumbnail')),
                ('earthquake', models.ForeignKey(to='realtime.Earthquake')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
