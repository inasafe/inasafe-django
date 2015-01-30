# coding=utf-8
"""Model class of custom user for InaSAFE User Map."""
import os
import uuid

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.gis.db import models
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError

from user_map.models.user_manager import CustomUserManager
from user_map.models.inasafe_role import InasafeRole
from user_map.models.osm_role import OsmRole
from user_map.utilities.utilities import wrap_number


def validate_image(fieldfile_obj):
    """Validate the image uploaded by user.

    :param fieldfile_obj: The object of the file field.
    :type fieldfile_obj: File (django.core.files)
    """
    file_size = fieldfile_obj.file.size
    size_limit_mb = 2.0
    size_limit = size_limit_mb * 1024 * 1024
    if file_size > size_limit:
        raise ValidationError(
            'Maximum image size is %s MB' % size_limit_mb)


def image_path(instance, file_name):
    """Return the proper image path to upload.

    :param file_name: The original file name.
    :type file_name: str
    """
    _, ext = os.path.splitext(file_name)

    file_name = '%s%s' % (uuid.uuid4().hex, ext)
    return os.path.join(
        'user_map',
        'images',
        file_name)


class User(AbstractBaseUser):
    """User class for InaSAFE User Map."""

    class Meta:
        """Meta class."""
        app_label = 'user_map'

    name = models.CharField(
        verbose_name='Name',
        help_text='Your name.',
        max_length=100,
        null=False,
        blank=False)
    email = models.EmailField(
        verbose_name='E-mail',
        help_text='Your email.',
        null=False,
        blank=False,
        unique=True)
    image = models.ImageField(
        verbose_name='Image',
        help_text='Your photo',
        upload_to=image_path,
        null=False,
        blank=True,
        validators=[validate_image])
    website = models.URLField(
        verbose_name='Website',
        help_text='Optional link to your personal or organisation web site.',
        null=False,
        blank=True)
    location = models.PointField(
        verbose_name='Location',
        help_text='Where are you?',
        srid=4326,
        max_length=255,
        null=False,
        blank=False)
    inasafe_roles = models.ManyToManyField(
        InasafeRole,
        verbose_name='InaSAFE Roles',
        blank=False)
    osm_roles = models.ManyToManyField(
        OsmRole,
        verbose_name='OSM Roles',
        blank=False)
    osm_username = models.CharField(
        verbose_name='OSM Username',
        help_text='Your OSM username.',
        max_length=100,
        null=False,
        blank=True)
    email_updates = models.BooleanField(
        verbose_name='Receiving Updates',
        help_text='Tick this to receive occasional news email messages.',
        default=False)
    date_joined = models.DateTimeField(
        verbose_name='Join Date',
        auto_now_add=True)
    is_certified_inasafe_trainer = models.BooleanField(
        verbose_name='Certified InaSAFE Trainer',
        help_text='Whether this user is a certified InaSAFE trainer or not.',
        default=False)
    is_certified_osm_trainer = models.BooleanField(
        verbose_name='Admin Status',
        help_text='Whether this user is a certified OSM trainer or not.',
        default=False)
    is_active = models.BooleanField(
        verbose_name='Active Status',
        help_text='Whether this user is still active or not (a user could be '
                  'banned or deleted).',
        default=True)
    is_admin = models.BooleanField(
        verbose_name='Admin Status',
        help_text='Whether this user is admin or not.',
        default=False)
    is_confirmed = models.BooleanField(
        verbose_name='Confirmation Status',
        help_text='Whether this user has approved their entry by email.',
        null=False,
        default=False)
    key = models.CharField(
        verbose_name='Confirmation Key',
        help_text='Confirmation key for user to activate their account.',
        max_length=40)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __unicode__(self):
        return self.name

    def get_full_name(self):
        """A longer formal identifier of the user.

        :return: The full name of a user.
        :rtype: str
        """
        return self.name

    def get_short_name(self):
        """A shorter formal identifier of the user.

        :return: The full name of a user.
        :rtype: str
        """
        return self.name

    def get_inasafe_roles(self):
        """The InaSAFE role(s) of the user."""
        return ', '.join([role.name for role in self.inasafe_roles.all()])

    def get_osm_roles(self):
        """The OSM role(s) of the user."""
        return ', '.join([role.name for role in self.osm_roles.all()])

    @property
    def is_staff(self):
        """The staff status of a user.

        Staff is determined by the admin status of a user.

        :return: True if the user is an admin, otherwise False.
        :rtype: bool
        """
        return self.is_admin

    # noinspection PyUnusedLocal
    def has_perm(self, perm, obj=None):
        """Returns true if the user has the named permission.

        :param perm: The permission.
        :type perm: str

        :param obj: The object that will be used to check the permission.
        :type obj: object

        :return: The permission status.
        :rtype: bool
        """
        return self.is_admin

    # noinspection PyUnusedLocal
    def has_module_perms(self, app_label):
        """Returns True if the user has permission to access models of the app.

        :param app_label: The application.
        :type app_label: str

        :return: The permission status.
        :rtype: bool
        """
        return self.is_admin


    def save(self, *args, **kwargs):
        """Override save method."""
        if not self.pk:
            # New object here
            self.key = get_random_string()
        else:
            # Saving a not new object
            user = User.objects.get(pk=self.pk)
            # Remove the old image if it's new image
            if user.image != self.image:
                user.image.delete(save=False)

        # Wrap location data
        self.location.x = wrap_number(self.location.x, [-180, 180])
        self.location.y = wrap_number(self.location.y, [-90, 90])

        super(User, self).save()
