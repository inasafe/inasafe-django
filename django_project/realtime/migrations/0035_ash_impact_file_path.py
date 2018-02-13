# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0034_auto_20180208_1327'),
    ]

    operations = [
        migrations.AddField(
            model_name='ash',
            name='impact_file_path',
            field=models.CharField(default=None, max_length=255, blank=True, help_text='Location of impact file.', null=True, verbose_name='Impact File path'),
        ),
    ]
