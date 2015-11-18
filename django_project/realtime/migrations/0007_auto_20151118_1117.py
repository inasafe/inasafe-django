# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0006_userpush'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='earthquakereport',
            unique_together=set([('earthquake', 'language')]),
        ),
    ]
