# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0059_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reporttemplate',
            name='hazard',
            field=models.CharField(default=None, help_text='The hazard type of the template.', max_length=25, verbose_name='Hazard Type', choices=[(b'earthquake', b'earthquake'), (b'flood', b'flood'), (b'ash', b'ash')]),
        ),
    ]
