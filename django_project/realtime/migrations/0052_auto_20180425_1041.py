# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0051_auto_20180321_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='coreflatpage',
            name='slug_id',
            field=models.CharField(choices=[(b'eq_landing_page', b'eq_landing_page'), (b'ash_landing_page', b'ash_landing_page'), (b'flood_landing_page', b'flood_landing_page'), (b'eq_about_page', b'eq_about_page'), (b'ash_about_page', b'ash_about_page'), (b'flood_about_page', b'flood_about_page')], max_length=30, blank=True, help_text=b'These slug ID will contains predetermined values', null=True, verbose_name=b'Slug ID used as reference for internal CMS'),
        ),
        migrations.AddField(
            model_name='coreflatpage',
            name='system_category',
            field=models.CharField(default=b'other', choices=[(b'landing_page', b'landing_page'), (b'about_page', b'about_page'), (b'other', b'other')], max_length=30, blank=True, help_text=b'Help categorizes this flat page for internal CMS', null=True, verbose_name=b'System category used for internal CMS'),
        ),
    ]
