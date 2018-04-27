# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0053_auto_20180425_2318'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='earthquake',
            name='analysis_task_id',
        ),
        migrations.RemoveField(
            model_name='earthquake',
            name='analysis_task_result',
        ),
        migrations.RemoveField(
            model_name='earthquake',
            name='analysis_task_status',
        ),
        migrations.RemoveField(
            model_name='earthquake',
            name='report_task_id',
        ),
        migrations.RemoveField(
            model_name='earthquake',
            name='report_task_result',
        ),
        migrations.RemoveField(
            model_name='earthquake',
            name='report_task_status',
        ),
        migrations.AddField(
            model_name='earthquakereport',
            name='report_task_id',
            field=models.CharField(default=b'', help_text='Task id for creating analysis report.', max_length=255, verbose_name='Report celery task id', blank=True),
        ),
        migrations.AddField(
            model_name='earthquakereport',
            name='report_task_result',
            field=models.TextField(default=b'', help_text='Task result of report generation', null=True, verbose_name='Report celery task result', blank=True),
        ),
        migrations.AddField(
            model_name='earthquakereport',
            name='report_task_status',
            field=models.CharField(default=b'None', help_text='Task status for creating analysis report.', max_length=30, verbose_name='Report celery task status', blank=True),
        ),
        migrations.AddField(
            model_name='impact',
            name='analysis_task_id',
            field=models.CharField(default=b'', help_text='Task id for running analysis', max_length=255, verbose_name='Analysis celery task id', blank=True),
        ),
        migrations.AddField(
            model_name='impact',
            name='analysis_task_result',
            field=models.TextField(default=b'', help_text='Task result of analysis run', null=True, verbose_name='Analysis celery task result', blank=True),
        ),
        migrations.AddField(
            model_name='impact',
            name='analysis_task_status',
            field=models.CharField(default=b'None', help_text='Task status for running analysis', max_length=30, verbose_name='Analysis celery task status', blank=True),
        ),
    ]
