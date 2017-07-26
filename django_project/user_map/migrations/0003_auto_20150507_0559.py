# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_map', '0002_populate_roles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_certified_osm_trainer',
            field=models.BooleanField(default=False, help_text=b'Whether this user is a certified OSM trainer or not.', verbose_name=b'Certified OSM Trainer'),
        ),
    ]
