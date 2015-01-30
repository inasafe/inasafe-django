# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from user_map.app_settings import INASAFE_ROLES, OSM_ROLES


def populate_roles(apps, schema_editor):
    """Populate roles from app setting.

    :param apps: App registry.
    :type apps: django.apps.apps

    :param schema_editor: Django db abstraction for turning model into db.
    :type schema_editor: django.db.backends.schema
    """
    # Populate InaSAFE Roles
    InasafeRole = apps.get_model('user_map', 'InasafeRole')
    for idx, inasafe_role in enumerate(INASAFE_ROLES):
        InasafeRole.objects.create(
            name=inasafe_role['name'],
            badge=inasafe_role['badge'],
            sort_number=(idx + 1))

    # Populate OSM Roles
    OsmRole = apps.get_model('user_map', 'OsmRole')
    for idx, osm_role in enumerate(OSM_ROLES):
        OsmRole.objects.create(
            name=osm_role['name'],
            badge=osm_role['badge'],
            sort_number=(idx + 1))

class Migration(migrations.Migration):

    dependencies = [
        ('user_map', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_roles)
    ]
