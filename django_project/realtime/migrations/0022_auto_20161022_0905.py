# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0021_auto_20160919_1754'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ash',
            options={'verbose_name_plural': 'Ashes'},
        ),
        migrations.AlterModelOptions(
            name='volcano',
            options={'verbose_name_plural': 'Volcanoes'},
        ),
        migrations.AddField(
            model_name='ash',
            name='eruption_height',
            field=models.IntegerField(default=0, verbose_name=b'Eruption height in meter'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ash',
            name='task_id',
            field=models.CharField(default=b'', help_text=b'Task id for processing', max_length=255, verbose_name=b'Celery task id', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ash',
            name='task_status',
            field=models.CharField(default=b'None', help_text=b'Task status for processing', max_length=30, verbose_name=b'Celery task status', blank=True),
            preserve_default=True,
        ),
    ]
