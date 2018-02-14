# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0035_ash_impact_file_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='ash',
            name='analysis_task_id',
            field=models.CharField(default=b'', help_text='Task id for running analysis', max_length=255, verbose_name='Analysis celery task id', blank=True),
        ),
        migrations.AddField(
            model_name='ash',
            name='analysis_task_status',
            field=models.CharField(default=b'None', help_text='Task status for running analysis', max_length=30, verbose_name='Analysis celery task status', blank=True),
        ),
    ]
