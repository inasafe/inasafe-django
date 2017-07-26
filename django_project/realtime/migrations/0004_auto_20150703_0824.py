# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0003_earthquakereport_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='earthquakereport',
            name='earthquake',
            field=models.ForeignKey(related_name='reports', to='realtime.Earthquake'),
            preserve_default=True,
        ),
    ]
