# uses noqa to disable false positive warning
# these needs to be included for django to detect
from realtime.models.earthquake import Earthquake  # noqa
from realtime.models.user_push import UserPush  # noqa
from realtime.models.flood import Flood, Boundary, FloodEventBoundary  # noqa

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
