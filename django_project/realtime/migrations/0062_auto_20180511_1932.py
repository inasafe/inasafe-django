# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0061_earthquakemigration_floodmigration'),
    ]

    operations = [
        migrations.AddField(
            model_name='earthquake',
            name='shake_grid_saved',
            field=models.BooleanField(default=False, verbose_name='Cache flag to tell that shakemap grid already saved.'),
        ),
        migrations.AddField(
            model_name='flood',
            name='flood_data_saved',
            field=models.BooleanField(default=False, verbose_name='Cache flag to tell that flood_data is saved.'),
        ),
    ]
