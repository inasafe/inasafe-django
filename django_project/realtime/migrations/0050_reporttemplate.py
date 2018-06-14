# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0049_auto_20180320_0406'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(help_text='The time the template uploaded.', verbose_name='Timestamp')),
                ('version', models.CharField(default=None, max_length=10, blank=True, help_text='Version number of the template.', null=True, verbose_name='Template version')),
                ('notes', models.CharField(default=None, max_length=255, blank=True, help_text='Notes of the report template.', null=True, verbose_name='Template Notes')),
                ('language', models.CharField(default=b'id', help_text='The language ID of the report', max_length=4, verbose_name='Language ID')),
                ('hazard', models.CharField(default=None, help_text='The hazard type of the template.', max_length=25, verbose_name='Hazard Type')),
                ('template_file', models.FileField(help_text='Template file formatted as qgis template file (*.qpt).', upload_to=b'', verbose_name='Template File')),
                ('owner', models.IntegerField(default=0, help_text='The owner/uploader of the template.', verbose_name='Owner')),
            ],
            options={
                'verbose_name_plural': 'Report Templates',
            },
        ),
    ]
