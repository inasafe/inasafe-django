# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0029_coreflatpage_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='coreflatpage',
            name='language',
            field=models.CharField(default=b'en', max_length=10, blank=True, help_text=b'Help tag the language of the code', null=True, verbose_name=b'Language code of the page'),
            preserve_default=True,
        ),
    ]
