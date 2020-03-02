# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0063_auto_20180604_0809'),
    ]

    operations = [
        migrations.AddField(
            model_name='flood',
            name='push_task_result',
            field=models.TextField(default=b'', help_text='Task result of GeoNode Push Task', null=True, verbose_name='Report push task result', blank=True),
        ),
        migrations.AddField(
            model_name='flood',
            name='push_task_status',
            field=models.CharField(default=None, max_length=255, blank=True, help_text='The Status for the GeoNode Push Task', null=True, verbose_name='GeoNode Push Task Status'),
        ),
    ]
