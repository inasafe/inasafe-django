# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0055_earthquake_has_corrected'),
    ]

    operations = [
        migrations.AddField(
            model_name='earthquake',
            name='mmi_layer_saved',
            field=models.BooleanField(default=False, verbose_name='Cache flag to tell that this shakemap already saved its contours.'),
        ),
    ]
