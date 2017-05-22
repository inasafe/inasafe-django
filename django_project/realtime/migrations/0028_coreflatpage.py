# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flatpages', '0001_initial'),
        ('realtime', '0027_flood_data_source'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoreFlatPage',
            fields=[
                ('flatpage_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='flatpages.FlatPage')),
                ('group', models.CharField(help_text=b'Help categorizes this flat page in a group', max_length=100, verbose_name=b'Group of FlatPage', blank=True)),
            ],
            options={
            },
            bases=('flatpages.flatpage',),
        ),
    ]
