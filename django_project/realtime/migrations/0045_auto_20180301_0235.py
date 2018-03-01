# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0044_flood_flood_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='impacteventboundary',
            name='affected',
            field=models.BooleanField(default=False, help_text='Affected status of the boundary impact', verbose_name='Affected status of the boundary impact'),
        ),
        migrations.AlterField(
            model_name='impacteventboundary',
            name='hazard_class',
            field=models.CharField(help_text='Hazard class in the given boundary', max_length=50, null=True, verbose_name='Hazard Class', blank=True),
        ),
    ]
