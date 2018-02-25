# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0039_auto_20180220_1713'),
    ]

    operations = [
        migrations.AddField(
            model_name='earthquake',
            name='analysis_task_result',
            field=models.TextField(default=b'', help_text='Task result of analysis run', null=True, verbose_name='Analysis celery task result', blank=True),
        ),
        migrations.AddField(
            model_name='earthquake',
            name='mmi_output_path',
            field=models.CharField(default=None, max_length=255, blank=True, help_text='MMI related file path location', null=True, verbose_name='MMI related file path'),
        ),
        migrations.AddField(
            model_name='earthquake',
            name='report_task_result',
            field=models.TextField(default=b'', help_text='Task result of report generation', null=True, verbose_name='Report celery task result', blank=True),
        ),
    ]
