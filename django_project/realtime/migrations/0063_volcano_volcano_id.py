# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0062_auto_20180511_1932'),
    ]

    operations = [
        migrations.AddField(
            model_name='volcano',
            name='volcano_id',
            field=models.CharField(default=b'', help_text='The ID of the volcano', max_length=50, verbose_name='The Volcano ID'),
        ),
    ]
