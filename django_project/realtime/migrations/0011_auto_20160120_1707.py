# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0010_auto_20151207_0914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boundary',
            name='name',
            field=models.CharField(help_text=b'Name entitled to this particular boundary', max_length=64, null=True, verbose_name=b'Boundary name', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='floodeventboundary',
            name='boundary',
            field=models.ForeignKey(related_name='flood_event', verbose_name=b'Boundary', to_field=b'upstream_id', to='realtime.Boundary', help_text=b'The linked boundary of the flood events'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='floodeventboundary',
            name='flood',
            field=models.ForeignKey(related_name='flood_event', verbose_name=b'Flood Event', to_field=b'event_id', to='realtime.Flood', help_text=b'The flood event of the linked boundary'),
            preserve_default=True,
        ),
    ]
