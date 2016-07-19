# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0014_auto_20160401_2003'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ash',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('volcano_name', models.CharField(help_text=b'The name of the volcano', max_length=b'30', verbose_name=b'The Volcano Name')),
                ('location', django.contrib.gis.db.models.fields.PointField(help_text=b'The location of the shake event in longitude and latitude.', srid=4326, max_length=255, verbose_name=b'Location')),
                ('alert_level', models.CharField(help_text=b'The alert level of the volcano ash event.', max_length=b'30', verbose_name=b'Alert Level')),
                ('hazard_file', models.FileField(help_text=b'Collection of hazard file in zip.', upload_to=b'ash/hazard_file/%Y/%m/%d', verbose_name=b'Hazard File')),
                ('eruption_height', models.FloatField(help_text=b'The height of the eruption in meter unit', verbose_name=b'Eruption Height')),
                ('event_time', models.DateTimeField(help_text=b'The time the ash happened.', verbose_name=b'Event Date and Time')),
                ('region', models.CharField(help_text=b'The region where the ash happened, e.g. Jawa Timur.', max_length=b'30', verbose_name=b'Region')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='floodeventboundary',
            options={'verbose_name_plural': 'Flood Event Boundaries'},
        ),
        migrations.AddField(
            model_name='earthquake',
            name='felt',
            field=models.BooleanField(default=False, help_text=b"Set to True if this particular event showed up as felt Earthquake in BMKG's List", verbose_name=b'Felt Earthquake'),
            preserve_default=True,
        ),
    ]
