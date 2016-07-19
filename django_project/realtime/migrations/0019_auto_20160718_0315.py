# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0018_auto_20160717_2030'),
    ]

    operations = [
        migrations.CreateModel(
            name='AshReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(default=b'en', help_text=b'The language ID of the report', max_length=4, verbose_name=b'Language ID')),
                ('report_map', models.FileField(help_text=b'The map impact report stored as PDF', upload_to=b'reports/ash/pdf', verbose_name=b'Map PDF Report')),
                ('ash', models.ForeignKey(related_name='reports', to='realtime.Ash')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='ashreport',
            unique_together=set([('ash', 'language')]),
        ),
    ]
