# coding=utf-8

from builtins import object
import logging

from django.contrib.gis.db import models

from realtime.app_settings import LOGGER_NAME
from realtime.models import Earthquake, Flood
from realtime.tasks import process_hazard_layer, process_impact_layer

LOGGER = logging.getLogger(LOGGER_NAME)


class EarthquakeMigration(models.Model):
    """This model will handle migration state of earthquake."""

    class Meta(object):
        app_label = 'realtime'

    event = models.ForeignKey(Earthquake, related_name='migration_state')
    migrated = models.BooleanField(
        default=False
    )
    has_shake_grid_in_raw_file = models.BooleanField(
        default=False
    )
    has_shake_grid_in_media_file = models.BooleanField(
        default=False
    )
    has_shake_grid_in_database = models.BooleanField(
        default=False
    )
    has_mmi_in_raw_file = models.BooleanField(
        default=False
    )
    has_mmi_in_media_file = models.BooleanField(
        default=False
    )
    has_mmi_in_database = models.BooleanField(
        default=False
    )
    shake_grid_migrated = models.BooleanField(
        default=False
    )
    mmi_migrated = models.BooleanField(
        default=False
    )

    def __unicode__(self):
        return ('EQ [{0}] hd [{1}] hm [{2}] hr [{3}] '
                'id [{4}] im [{5}] ir [{6}]').format(
            self.event.shake_id,
            self.has_shake_grid_in_database,
            self.has_shake_grid_in_media_file,
            self.has_shake_grid_in_raw_file,
            self.has_mmi_in_database,
            self.has_mmi_in_media_file,
            self.has_mmi_in_raw_file
        )

    def check_shake_grid_status(self):
        event = self.event
        if event.shake_grid_xml:
            self.has_shake_grid_in_database = True

        if event.shake_grid:
            self.has_shake_grid_in_media_file = True

        self.save()

    def mark_shake_grid_migrated(self):
        if not self.has_shake_grid_in_database:
            return False

        if self.has_shake_grid_in_media_file:
            self.event.shake_grid.delete(save=True)
            self.has_shake_grid_in_media_file = False

        self.shake_grid_migrated = True
        self.save()
        return True

    def check_mmi_status(self):
        event = self.event
        if event.mmi_layer_saved and event.contours.all():
            self.has_mmi_in_database = True

        if event.mmi_output:
            self.has_mmi_in_media_file = True

        self.save()

    def mark_mmi_migrated(self):
        if not self.has_mmi_in_database:
            return False

        if self.has_mmi_in_media_file:
            self.event.mmi_output.delete(save=True)
            self.has_mmi_in_media_file = False

        self.mmi_migrated = True
        self.save()
        return True

    def mark_migrated(self):
        shake_migrated = self.mark_shake_grid_migrated()
        mmi_migrated = self.mark_mmi_migrated()
        if shake_migrated and mmi_migrated:
            self.migrated = True
            self.save()
            return True
        return False

    @staticmethod
    def scan_migration_state():
        """Scan current migration state and mark migrated event."""

        events = Earthquake.objects.all()
        for _e in events.iterator():
            e = _e
            """:type: Earthquake"""

            if not e.inasafe_version:
                e.inasafe_version = '3.5'
                e.save()

            if not e.migration_state.all():
                migration_state = EarthquakeMigration.objects.create(
                    event=e)
                e.refresh_from_db()
            else:
                migration_state = e.migration_state.first()

            migration_state.check_shake_grid_status()
            migration_state.check_mmi_status()

    def migrate_shake_grid(self):

        if self.has_shake_grid_in_database:
            return

        event = self.event
        if self.has_shake_grid_in_media_file:

            xml_content = event.shake_grid.read()
            event.shake_grid_xml = xml_content
            event.shake_grid_saved = True
            event.save()

            self.check_shake_grid_status()

            self.mark_shake_grid_migrated()


class FloodMigration(models.Model):
    """This model will handle migration state of flood."""

    class Meta(object):
        app_label = 'realtime'

    event = models.ForeignKey(Flood, related_name='migration_state')
    migrated = models.BooleanField(
        default=False
    )
    has_hazard_in_raw_file = models.BooleanField(
        default=False
    )
    has_hazard_in_media_file = models.BooleanField(
        default=False
    )
    has_hazard_in_database = models.BooleanField(
        default=False
    )
    has_impact_in_raw_file = models.BooleanField(
        default=False
    )
    has_impact_in_media_file = models.BooleanField(
        default=False
    )
    has_impact_in_database = models.BooleanField(
        default=False
    )
    hazard_migrated = models.BooleanField(
        default=False
    )
    impact_migrated = models.BooleanField(
        default=False
    )

    def __unicode__(self):
        return (
            'Flood [{0}] hd [{1}] hm [{2}] hr [{3}] '
            'id [{4}] im [{5}] ir [{6}]').format(
            self.event.event_id_formatted,
            self.has_hazard_in_database,
            self.has_hazard_in_media_file,
            self.has_hazard_in_raw_file,
            self.has_impact_in_database,
            self.has_impact_in_media_file,
            self.has_impact_in_raw_file
        )

    def check_hazard_status(self):
        event = self.event
        if event.flooded_boundaries:
            self.has_hazard_in_database = True

        if event.hazard_layer:
            self.has_hazard_in_media_file = True

        self.save()

    def mark_hazard_migrated(self):
        if not self.has_hazard_in_database:
            return False

        if self.has_hazard_in_media_file:
            self.event.hazard_layer.delete(save=True)
            self.has_hazard_in_media_file = False

        self.hazard_migrated = True
        self.save()
        return True

    def check_impact_status(self):
        event = self.event
        if event.impact_event.all():
            self.has_impact_in_database = True

        if event.impact_layer:
            self.has_impact_in_media_file = True

        self.save()

    def mark_impact_migrated(self):
        if not self.has_impact_in_database:
            return False

        if self.has_impact_in_media_file:
            self.event.impact_layer.delete(save=True)
            self.has_impact_in_media_file = False

        self.impact_migrated = True
        self.save()
        return True

    def mark_migrated(self):
        hazard_migrated = self.mark_hazard_migrated()
        impact_migrated = self.mark_impact_migrated()
        if hazard_migrated and impact_migrated:
            self.migrated = True
            self.save()
            return True
        return False

    @staticmethod
    def scan_migration_state():
        """Scan current migration state and mark migrated event."""

        events = Flood.objects.all()
        for _e in events.iterator():
            e = _e
            """:type: Flood"""

            if not e.inasafe_version:
                e.inasafe_version = '3.5'
                e.save()

            if not e.migration_state.all():
                migration_state = FloodMigration.objects.create(
                    event=e)
                e.refresh_from_db()
            else:
                migration_state = e.migration_state.first()

            migration_state.check_hazard_status()
            migration_state.check_impact_status()

    def migrate_hazard(self):

        if self.has_hazard_in_database:
            return

        event = self.event
        if self.has_hazard_in_media_file:

            try:
                process_hazard_layer(event)
            except Exception as e:
                LOGGER.exception(e)

            self.check_hazard_status()

            self.mark_hazard_migrated()

    def migrate_impact(self):

        if self.has_impact_in_database:
            return

        event = self.event
        if self.has_impact_in_media_file:

            try:
                process_impact_layer(event)
            except Exception as e:
                LOGGER.exception(e)

            self.check_impact_status()

            self.mark_impact_migrated()
