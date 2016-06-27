# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0014_auto_20160401_2003'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='floodeventboundary',
            options={'verbose_name_plural': 'Flood Event Boundaries'},
        ),
        migrations.AddField(
            model_name='earthquake',
            name='felt',
            field=models.BooleanField(default=False, help_text=b"Set to True if this particular event showed up as felt Earthquake in BMKG's List", verbose_name=b'Felt Earthquake'),
            preserve_default=True,
        ),
    ]
