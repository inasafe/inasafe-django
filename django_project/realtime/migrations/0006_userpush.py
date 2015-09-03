# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('realtime', '0005_create_rest_groups'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPush',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_shakemap_push', models.DateTimeField(help_text=b'Date and time of last shakemap push made by user', verbose_name=b'Last shakemap push')),
                ('last_rest_push', models.DateTimeField(help_text=b'Date and time of last Earthquake REST post made by user', verbose_name=b'Last REST push')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
