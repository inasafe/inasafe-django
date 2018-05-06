# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0060_auto_20180506_1815'),
    ]

    operations = [
        migrations.CreateModel(
            name='EarthquakeMigration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('migrated', models.BooleanField(default=False)),
                ('has_shake_grid_in_raw_file', models.BooleanField(default=False)),
                ('has_shake_grid_in_media_file', models.BooleanField(default=False)),
                ('has_shake_grid_in_database', models.BooleanField(default=False)),
                ('has_mmi_in_raw_file', models.BooleanField(default=False)),
                ('has_mmi_in_media_file', models.BooleanField(default=False)),
                ('has_mmi_in_database', models.BooleanField(default=False)),
                ('shake_grid_migrated', models.BooleanField(default=False)),
                ('mmi_migrated', models.BooleanField(default=False)),
                ('event', models.ForeignKey(related_name='migration_state', to='realtime.Earthquake')),
            ],
        ),
        migrations.CreateModel(
            name='FloodMigration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('migrated', models.BooleanField(default=False)),
                ('has_hazard_in_raw_file', models.BooleanField(default=False)),
                ('has_hazard_in_media_file', models.BooleanField(default=False)),
                ('has_hazard_in_database', models.BooleanField(default=False)),
                ('has_impact_in_raw_file', models.BooleanField(default=False)),
                ('has_impact_in_media_file', models.BooleanField(default=False)),
                ('has_impact_in_database', models.BooleanField(default=False)),
                ('hazard_migrated', models.BooleanField(default=False)),
                ('impact_migrated', models.BooleanField(default=False)),
                ('event', models.ForeignKey(related_name='migration_state', to='realtime.Flood')),
            ],
        ),
    ]
