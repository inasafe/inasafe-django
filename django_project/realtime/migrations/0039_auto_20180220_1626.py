# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0038_auto_20180219_1113'),
    ]

    operations = [
        migrations.AddField(
            model_name='flood',
            name='analysis_task_id',
            field=models.CharField(default=b'', help_text='Task id for running analysis', max_length=255, verbose_name='Analysis celery task id', blank=True),
        ),
        migrations.AddField(
            model_name='flood',
            name='analysis_task_status',
            field=models.CharField(default=b'None', help_text='Task status for running analysis', max_length=30, verbose_name='Analysis celery task status', blank=True),
        ),
        migrations.AddField(
            model_name='flood',
            name='impact_file_path',
            field=models.CharField(default=None, max_length=255, blank=True, help_text='Location of impact file.', null=True, verbose_name='Impact File path'),
        ),
        migrations.AddField(
            model_name='flood',
            name='report_task_id',
            field=models.CharField(default=b'', help_text='Task id for creating analysis report.', max_length=255, verbose_name='Report celery task id', blank=True),
        ),
        migrations.AddField(
            model_name='flood',
            name='report_task_status',
            field=models.CharField(default=b'None', help_text='Task status for creating analysis report.', max_length=30, verbose_name='Report celery task status', blank=True),
        ),
        migrations.AddField(
            model_name='flood',
            name='task_id',
            field=models.CharField(default=b'', help_text='Task id for processing', max_length=255, verbose_name='Celery task id', blank=True),
        ),
        migrations.AddField(
            model_name='flood',
            name='task_status',
            field=models.CharField(default=b'None', help_text='Task status for processing', max_length=30, verbose_name='Celery task status', blank=True),
        ),
    ]
