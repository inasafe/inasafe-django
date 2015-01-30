# coding=utf-8
"""Model factories definition for models."""
from django.contrib.gis.geos import Point
import factory
from factory import DjangoModelFactory

from user_map.models import InasafeRole, OsmRole, User


class InasafeRoleFactory(DjangoModelFactory):
    """Factory class for InaSAFE Role model."""
    class Meta:
        """Meta definition."""
        model = InasafeRole

    name = factory.Sequence(lambda n: 'InaSAFE Role %s' % n)
    badge = factory.Sequence(lambda n: '/image/badge-%s' % n)
    sort_number = factory.Sequence(lambda n: n)


class OsmRoleFactory(DjangoModelFactory):
    """Factory class for OSM Role model."""
    class Meta:
        """Meta definition."""
        model = OsmRole

    name = factory.Sequence(lambda n: 'OSM Role %s' % n)
    badge = factory.Sequence(lambda n: '/image/badge-%s' % n)
    sort_number = factory.Sequence(lambda n: n)


class UserFactory(DjangoModelFactory):
    """Factory class for User Model"""
    class Meta:
        """"Meta definition."""
        model = User
        django_get_or_create = ('email',)

    # Taking others as default value defined in model but not these:
    name = 'John Doe'
    email = factory.Sequence(lambda n: 'john.doe%s@example.com' % n)
    password = factory.PostGenerationMethodCall(
        'set_password', 'default_password')
    location = Point(105.567, 123)

    @classmethod
    def _prepare(cls, create, **kwargs):
        inasafe_role_1 = InasafeRoleFactory()
        inasafe_role_2 = InasafeRoleFactory()
        osm_role_1 = OsmRoleFactory()
        osm_role_2 = OsmRoleFactory()

        user = super(UserFactory, cls)._prepare(create, **kwargs)

        user.inasafe_roles.add(inasafe_role_1)
        user.inasafe_roles.add(inasafe_role_2)

        user.osm_roles.add(osm_role_1)
        user.osm_roles.add(osm_role_2)
        return user
