# coding=utf-8
from getpass import getpass

from django.contrib.auth.models import Group
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from realtime.app_settings import REST_GROUP
from user_map.models.user import User

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/09/15'


class Command(BaseCommand):
    """Create Realtime REST user.

    This user can be able to use REST API that modifies data
    (POST, PUT, DELETE)
    """

    def handle(self, *args, **options):
        realtime_group = Group.objects.get(name=REST_GROUP)
        username = raw_input('Username : ')
        email = raw_input('Email : ')
        password = getpass()
        done = False

        while not done:
            location = raw_input(
                'Location (lon lat), leave blank for default : ')
            if not location:
                location = Point(106.8222713, -6.1856145)
                done = True
            else:
                try:
                    location = location.split()
                    if not len(location):
                        raise ValueError()

                    location = Point(float(location[0]), float(location[1]))
                    done = True
                except ValueError:
                    print 'Give location in form (lon lat) without brace.'
                    pass

        new_user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            location=location,
            email_updates=False,
        )

        if new_user:
            new_user.groups.add(realtime_group)
            new_user.save()
            print 'User is created'
