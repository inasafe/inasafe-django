# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0036_auto_20180214_0226'),
    ]

    operations = [
        migrations.AddField(
            model_name='ash',
            name='report_task_id',
            field=models.CharField(default=b'', help_text='Task id for creating analysis report.', max_length=255, verbose_name='Report celery task id', blank=True),
        ),
        migrations.AddField(
            model_name='ash',
            name='report_task_status',
            field=models.CharField(default=b'None', help_text='Task status for creating analysis report.', max_length=30, verbose_name='Report celery task status', blank=True),
        ),
    ]
