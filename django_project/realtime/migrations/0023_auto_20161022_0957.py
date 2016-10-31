# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0022_auto_20161022_0905'),
    ]

    operations = [
        migrations.AddField(
            model_name='volcano',
            name='district',
            field=models.CharField(help_text=b'The district where the volcano located', max_length=50, verbose_name=b'The district name', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='volcano',
            name='province',
            field=models.CharField(help_text=b'The province where the volcano located', max_length=50, verbose_name=b'The province name', blank=True),
            preserve_default=True,
        ),
    ]
