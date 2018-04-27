# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0054_auto_20180426_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='earthquake',
            name='has_corrected',
            field=models.BooleanField(default=False, verbose_name='Cache flag to tell that this shakemap has a corrected version.'),
        ),
    ]
