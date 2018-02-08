# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0033_auto_20180202_0723'),
    ]

    operations = [
        migrations.AddField(
            model_name='ash',
            name='hazard_path',
            field=models.CharField(default=None, max_length=255, blank=True, help_text='Location of hazard layer', null=True, verbose_name='Hazard Layer path'),
        ),
        migrations.AddField(
            model_name='ash',
            name='inasafe_version',
            field=models.CharField(default=None, max_length=10, blank=True, help_text='InaSAFE version being used', null=True, verbose_name='InaSAFE version'),
        ),
        migrations.AddField(
            model_name='earthquake',
            name='generated_time',
            field=models.DateTimeField(default=None, help_text='The time the shake report generated.', null=True, verbose_name='Report Generated Date and Time'),
        ),
        migrations.AddField(
            model_name='earthquake',
            name='hazard_path',
            field=models.CharField(default=None, max_length=255, blank=True, help_text='Location of hazard layer', null=True, verbose_name='Hazard Layer path'),
        ),
        migrations.AddField(
            model_name='earthquake',
            name='inasafe_version',
            field=models.CharField(default=None, max_length=10, blank=True, help_text='InaSAFE version being used', null=True, verbose_name='InaSAFE version'),
        ),
        migrations.AddField(
            model_name='earthquake',
            name='source_type',
            field=models.CharField(default=b'initial', help_text='Source type of shake grid', max_length=30, verbose_name='Source Type'),
        ),
        migrations.AddField(
            model_name='flood',
            name='hazard_path',
            field=models.CharField(default=None, max_length=255, blank=True, help_text='Location of hazard layer', null=True, verbose_name='Hazard Layer path'),
        ),
        migrations.AddField(
            model_name='flood',
            name='inasafe_version',
            field=models.CharField(default=None, max_length=10, blank=True, help_text='InaSAFE version being used', null=True, verbose_name='InaSAFE version'),
        ),
        migrations.AddField(
            model_name='flood',
            name='source_type',
            field=models.CharField(default=b'petabencana', help_text='Source type of shake grid', max_length=30, verbose_name='Source Type'),
        ),
        migrations.AlterField(
            model_name='earthquake',
            name='shake_id',
            field=models.CharField(help_text='The Shake ID, which represents the time of the event.', max_length=b'14', verbose_name='The Shake ID'),
        ),
    ]
