# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0050_reporttemplate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reporttemplate',
            name='template_file',
            field=models.TextField(help_text='Template file formatted as qgis template file (*.qpt).', verbose_name='Template File'),
        ),
    ]
