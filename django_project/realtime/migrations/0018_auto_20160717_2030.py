# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0017_volcano'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ash',
            name='eruption_height',
        ),
        migrations.RemoveField(
            model_name='ash',
            name='location',
        ),
        migrations.RemoveField(
            model_name='ash',
            name='region',
        ),
        migrations.RemoveField(
            model_name='ash',
            name='volcano_name',
        ),
        migrations.AddField(
            model_name='ash',
            name='volcano',
            field=models.ForeignKey(related_name='ash', to='realtime.Volcano', null=True),
            preserve_default=True,
        ),
    ]
