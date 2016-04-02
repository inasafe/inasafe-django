# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0013_auto_20160401_0848'),
    ]

    operations = [
        migrations.AlterField(
            model_name='floodeventboundary',
            name='boundary',
            field=models.ForeignKey(related_name='flood_event',
                                    verbose_name=b'Boundary',
                                    to='realtime.Boundary',
                                    help_text=b'The linked boundary of the flood events'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='boundary',
            name='upstream_id',
            field=models.CharField(help_text=b'ID used by upstream data source to identify boundaries', max_length=64, verbose_name=b'Upstream ID'),
            preserve_default=True,
        ),
    ]
