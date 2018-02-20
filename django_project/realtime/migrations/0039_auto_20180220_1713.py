# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0038_auto_20180220_0953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='earthquake',
            name='generated_time',
            field=models.DateTimeField(default=None, help_text='The time the shake report generated.', null=True, verbose_name='Report Generated Date and Time', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='earthquake',
            unique_together=set([('shake_id', 'source_type')]),
        ),
    ]
