# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0011_auto_20160120_1707'),
    ]

    operations = [
        migrations.AddField(
            model_name='earthquake',
            name='shake_grid',
            field=models.FileField(help_text=b'The Shake Grid to process', upload_to=b'', null=True, verbose_name=b'Shake Grid XML File', blank=True),
            preserve_default=True,
        ),
    ]
