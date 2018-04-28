# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0056_earthquake_mmi_layer_saved'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flood',
            name='analysis_task_id',
        ),
        migrations.RemoveField(
            model_name='flood',
            name='analysis_task_result',
        ),
        migrations.RemoveField(
            model_name='flood',
            name='analysis_task_status',
        ),
        migrations.RemoveField(
            model_name='flood',
            name='impact_file_path',
        ),
        migrations.RemoveField(
            model_name='flood',
            name='report_task_id',
        ),
        migrations.RemoveField(
            model_name='flood',
            name='report_task_result',
        ),
        migrations.RemoveField(
            model_name='flood',
            name='report_task_status',
        ),
        migrations.AddField(
            model_name='floodreport',
            name='report_task_id',
            field=models.CharField(default=b'', help_text='Task id for creating analysis report.', max_length=255, verbose_name='Report celery task id', blank=True),
        ),
        migrations.AddField(
            model_name='floodreport',
            name='report_task_result',
            field=models.TextField(default=b'', help_text='Task result of report generation', null=True, verbose_name='Report celery task result', blank=True),
        ),
        migrations.AddField(
            model_name='floodreport',
            name='report_task_status',
            field=models.CharField(default=b'None', help_text='Task status for creating analysis report.', max_length=30, verbose_name='Report celery task status', blank=True),
        ),
    ]
