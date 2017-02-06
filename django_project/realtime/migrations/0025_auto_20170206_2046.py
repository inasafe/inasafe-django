# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0024_auto_20170206_2044'),
    ]

    operations = [
        migrations.AddField(
            model_name='flood',
            name='boundary_flooded',
            field=models.IntegerField(default=0, help_text=b'Total boundary affected by flood', verbose_name=b'Total boundary flooded'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flood',
            name='total_affected',
            field=models.IntegerField(default=0, help_text=b'Total affected people by flood', verbose_name=b'Total affected people by flood'),
            preserve_default=True,
        ),
    ]
