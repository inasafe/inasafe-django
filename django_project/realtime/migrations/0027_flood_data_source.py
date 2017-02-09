# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0026_auto_20170209_1905'),
    ]

    operations = [
        migrations.AddField(
            model_name='flood',
            name='data_source',
            field=models.CharField(default=None, max_length=255, blank=True, help_text=b'The source of the hazard data used for analysis', null=True, verbose_name=b'The source of hazard data'),
            preserve_default=True,
        ),
    ]
