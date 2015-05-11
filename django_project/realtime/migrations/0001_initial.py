# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Earthquake',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shake_id', models.CharField(help_text=b'The Shake ID, which represents the time of the event.', unique=True, max_length=b'14', verbose_name=b'The Shake ID')),
                ('magnitude', models.FloatField(help_text=b'The magnitude of the event.', verbose_name=b'The magnitude')),
                ('time', models.DateTimeField(help_text=b'The time the shake happened.', verbose_name=b'Date and Time')),
                ('depth', models.FloatField(help_text=b'The depth of the event in km unit.', verbose_name=b'The depth')),
                ('location', django.contrib.gis.db.models.fields.PointField(help_text=b'The location of the shake event in longitude and latitude.', srid=4326, max_length=255, verbose_name=b'Location')),
                ('location_description', models.CharField(help_text=b'The description of the location e.g "Bali".', max_length=255, verbose_name=b'Location Description')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
