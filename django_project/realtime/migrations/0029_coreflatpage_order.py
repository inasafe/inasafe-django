# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realtime', '0028_coreflatpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='coreflatpage',
            name='order',
            field=models.IntegerField(default=0, help_text=b'Help manage the order of the page as shown in the nav bar menu. Smaller means on top. Pages shown in navbar sorted by decreasing order value.', verbose_name=b'Order of the page'),
            preserve_default=True,
        ),
    ]
