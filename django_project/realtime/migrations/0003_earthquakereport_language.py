# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0002_earthquakereport'),
    ]

    operations = [
        migrations.AddField(
            model_name='earthquakereport',
            name='language',
            field=models.CharField(default=b'id', help_text=b'The language ID of the report', max_length=4, verbose_name=b'Language ID'),
            preserve_default=True,
        ),
    ]
