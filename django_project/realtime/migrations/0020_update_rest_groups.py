# coding=utf-8

from django.apps import apps as apps_registry
from django.contrib.auth.management import create_permissions
from django.contrib.contenttypes.management import update_contenttypes

from django.db import migrations
from realtime.app_settings import REST_GROUP, VOLCANO_GROUP, ASH_GROUP

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/3/15'


def create_realtime_rest_group(apps, schema_editor):
    """Populate Groups for volcano ash realtime group.

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
    group_list = [
        (REST_GROUP, [
            'ash',
            'floodreport',
            'earthquakereport',
            'impacteventboundary',
            'flood',
            'userpush',
            'boundary',
            'boundaryalias',
            'floodeventboundary',
            'earthquake',
            'volcano',
            'ashreport'
        ]),
        (VOLCANO_GROUP, [
            'volcano',
        ]),
        (ASH_GROUP, [
            'ash',
            'ashreport',
        ]),
    ]

    for g in group_list:
        try:
            realtime_group = Group.objects.get(name=g[0])
        except Group.DoesNotExist:
            realtime_group = Group.objects.create(name=g[0])

        Permission = apps.get_model('auth', 'Permission')
        for m in g[1]:
            realtime_permissions = Permission.objects.filter(
                content_type__app_label='realtime',
                content_type__model=m)
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
    group_list = [
        REST_GROUP,
        VOLCANO_GROUP,
        ASH_GROUP,
    ]
    for g in group_list:
        realtime_group = Group.objects.get(name=g)
        User = apps.get_model('user_map', 'User')
        users = User.objects.filter(groups__name=g)
        for user in users:
            user.groups.remove(realtime_group)
            user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('contenttypes', '0001_initial'),
        ('user_map', '0004_auto_20150703_0824'),
        ('realtime', '0019_auto_20160718_0315'),
    ]

    operations = [
        migrations.RunPython(create_realtime_rest_group,
                             delete_realtime_rest_group)
    ]
