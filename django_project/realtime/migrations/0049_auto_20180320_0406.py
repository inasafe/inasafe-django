# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0048_auto_20180315_2120'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='earthquake',
            options={'ordering': ['-time', '-shake_id', '-source_type']},
        ),
        migrations.AlterField(
            model_name='earthquake',
            name='shake_id',
            field=models.CharField(help_text='The Shake ID, which represents the time of the event.', max_length=50, verbose_name='The Shake ID'),
        ),
    ]
