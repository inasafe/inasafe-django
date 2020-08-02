# coding=utf-8
"""Custom User Manager for user of InaSAFE User Map."""
from builtins import object
from django.contrib.gis.db.models import GeoManager
from django.contrib.auth.models import BaseUserManager
from django.contrib.gis.geos import Point
from django.utils.crypto import get_random_string


class CustomUserManager(BaseUserManager, GeoManager):
    """Custom user manager for user map."""
    class Meta(object):
        """Meta class."""
        app_label = 'user_map'

    def create_user(
            self,
            username=None,
            email=None,
            password=None,
            location=None,
            email_updates=None,
            website='',
            **kwargs):
        """Create and save a User.

        :param username: The name of the user.
        :type username: str

        :param email: The email of the user.
        :type email: str

        :param location: The location of the user in (long, lat)
        :type location: Point

        :param email_updates: The status email_updates of the user.
        :type email_updates: bool

        :param website: The website of the user.
        :type website: str

        :param password: The password of the user.
        :type password: str
        """
        if not username:
            raise ValueError('User must have name.')

        if not email:
            raise ValueError('User must have an email address.')

        if not location:
            raise ValueError('User must have location.')

        if email_updates is None:
            raise ValueError('User must have email_updates status.')

        user = self.model(
            name=username,
            email=self.normalize_email(email),
            location=location,
            email_updates=email_updates,
            website=website,
            key=get_random_string(),
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, name, email, password, **kwargs):
        """Create and save a superuser.

        :param name: The name of the superuser.
        :type name: str

        :param email: The email of the superuser.
        :type email: str

        :param password: The password of the superuser.
        :type password:  str
        """
        # Use predefined location, role, email_updates, is_active, is_admin
        location = Point(106.8, -6.2)

        user = self.create_user(
            name,
            email,
            location=location,
            email_updates=True,
            password=password)
        user.email_updates = True
        user.is_confirmed = True
        user.is_active = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
