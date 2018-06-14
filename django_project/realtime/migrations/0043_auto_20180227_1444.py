# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0042_auto_20180227_1430'),
    ]

    operations = [
        migrations.AddField(
            model_name='flood',
            name='analysis_task_result',
            field=models.TextField(default=b'', help_text='Task result of analysis run', null=True, verbose_name='Analysis celery task result', blank=True),
        ),
        migrations.AddField(
            model_name='flood',
            name='report_task_result',
            field=models.TextField(default=b'', help_text='Task result of report generation', null=True, verbose_name='Report celery task result', blank=True),
        ),
    ]
