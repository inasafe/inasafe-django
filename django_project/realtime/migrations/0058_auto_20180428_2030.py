# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0057_auto_20180428_1721'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ash',
            name='analysis_task_id',
        ),
        migrations.RemoveField(
            model_name='ash',
            name='analysis_task_result',
        ),
        migrations.RemoveField(
            model_name='ash',
            name='analysis_task_status',
        ),
        migrations.RemoveField(
            model_name='ash',
            name='impact_file_path',
        ),
        migrations.RemoveField(
            model_name='ash',
            name='report_task_id',
        ),
        migrations.RemoveField(
            model_name='ash',
            name='report_task_result',
        ),
        migrations.RemoveField(
            model_name='ash',
            name='report_task_status',
        ),
        migrations.AddField(
            model_name='ashreport',
            name='report_task_id',
            field=models.CharField(default=b'', help_text='Task id for creating analysis report.', max_length=255, verbose_name='Report celery task id', blank=True),
        ),
        migrations.AddField(
            model_name='ashreport',
            name='report_task_result',
            field=models.TextField(default=b'', help_text='Task result of report generation', null=True, verbose_name='Report celery task result', blank=True),
        ),
        migrations.AddField(
            model_name='ashreport',
            name='report_task_status',
            field=models.CharField(default=b'None', help_text='Task status for creating analysis report.', max_length=30, verbose_name='Report celery task status', blank=True),
        ),
        migrations.AlterField(
            model_name='ashreport',
            name='language',
            field=models.CharField(default=b'id', help_text='The language ID of the report', max_length=4, verbose_name='Language ID'),
        ),
    ]
