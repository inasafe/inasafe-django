# -*- coding: utf-8 -*-
from django.apps import apps as apps_registry
from django.contrib.auth.management import create_permissions
from django.contrib.contenttypes.management import update_contenttypes

from django.db import migrations
from realtime.app_settings import REST_GROUP


def create_realtime_rest_group(apps, schema_editor):
    """Populate Groups for realtime group.

    :param apps: App registry.
    :type apps: django.apps.apps

    :param schema_editor: Django db abstraction for turning model into db.
    :type schema_editor: django.db.backends.schema
    """
    # import apps registry, somehow it was only loaded fully from import
    realtime_app_config = apps_registry.get_app_config('realtime')
    # update content types
    update_contenttypes(realtime_app_config, interactive=False)
    # update permissions
    create_permissions(realtime_app_config, interactive=False)
    Group = apps.get_model('auth', 'Group')
    Group.objects.create(name=REST_GROUP)
    realtime_group = Group.objects.get(name=REST_GROUP)
    Permission = apps.get_model('auth', 'Permission')
    realtime_permissions = Permission.objects.filter(
        content_type__app_label='realtime')
    realtime_group.permissions.add(*realtime_permissions)
    realtime_group.save()


def delete_realtime_rest_group(apps, schema_editor):
    """De-Populate Groups for realtime group.

    :param apps: App registry.
    :type apps: django.apps.apps

    :param schema_editor: Django db abstraction for turning model into db.
    :type schema_editor: django.db.backends.schema
    """
    Group = apps.get_model('auth', 'Group')
    realtime_group = Group.objects.get(name=REST_GROUP)
    User = apps.get_model('user_map', 'User')
    users = User.objects.filter(groups__name=REST_GROUP)
    for user in users:
        user.groups.remove(realtime_group)
        user.save()
    realtime_group.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('contenttypes', '0001_initial'),
        ('user_map', '0004_auto_20150703_0824'),
        ('realtime', '0004_auto_20150703_0824'),
    ]

    operations = [
        migrations.RunPython(create_realtime_rest_group,
                             delete_realtime_rest_group)
    ]
