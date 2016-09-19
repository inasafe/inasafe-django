# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0020_update_rest_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='ash',
            name='task_id',
            field=models.CharField(default=b'', help_text=b'Task id for processing', max_length=255, verbose_name=b'Celery task id'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ash',
            name='task_status',
            field=models.CharField(default=b'None', help_text=b'Task status for processing', max_length=30, verbose_name=b'Celery task status'),
            preserve_default=True,
        ),
    ]
