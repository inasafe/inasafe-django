# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0030_coreflatpage_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='ash',
            name='event_time_zone_offset',
            field=models.IntegerField(default=0, help_text='The time zone offset of event time.', verbose_name='Time Zone Offset'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ash',
            name='event_time_zone_string',
            field=models.CharField(default=b'UTC', help_text='The time zone string of event time.', max_length=255, verbose_name='Time Zone String'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='coreflatpage',
            name='language',
            field=models.CharField(default=b'en', choices=[(b'en', 'English'), (b'id', 'Indonesian')], max_length=10, blank=True, help_text=b'Help tag the language of the code', null=True, verbose_name=b'Language code of the page'),
            preserve_default=True,
        ),
    ]
