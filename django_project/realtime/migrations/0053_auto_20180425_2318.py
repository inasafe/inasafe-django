# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('realtime', '0052_auto_20180425_1041'),
    ]

    operations = [
        migrations.CreateModel(
            name='Impact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('impact_file_path', models.CharField(default=None, max_length=255, blank=True, help_text='Location of impact file.', null=True, verbose_name='Impact File path')),
                ('language', models.CharField(default=b'id', help_text='The language ID of the report', max_length=4, verbose_name='Language ID')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.RemoveField(
            model_name='earthquake',
            name='impact_file_path',
        ),
    ]
