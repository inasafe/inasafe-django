# coding=utf-8
"""InaSAFE Django task related to GeoNode upload."""
from __future__ import absolute_import
import logging

from celery import chain

from core.celery_app import app

from realtime.models.ash import Ash
from realtime.app_settings import LOGGER_NAME
from realtime.tasks.headless.inasafe_wrapper import push_to_geonode

LOGGER = logging.getLogger(LOGGER_NAME)
GEONODE_PUSH_SUCCESS = 0


@app.task(queue='inasafe-django')
def handle_push_to_geonode(push_result, hazard_class, hazard_event_id):
    """Handle geonode push result."""
    hazard = hazard_class.objects.get(id=hazard_event_id)
    task_state = 'FAILURE'
    if not push_result:
        task_state = 'FAILURE'
    elif push_result['status'] == GEONODE_PUSH_SUCCESS:
        task_state = 'SUCCESS'
    hazard.push_task_status = task_state
    hazard.push_task_result = push_result
    hazard.save()


@app.task(queue='inasafe-django')
def push_hazard_to_geonode(hazard_class, hazard_event):
    """Upload layer to geonode and update the status of hazard."""
    LOGGER.info('Push layer to geonode.')
    hazard_layer_uri = hazard_event.hazard_path
    hazard_event_id = hazard_event.id

    tasks_chain = chain(
        # Push to layer to geonode
        push_to_geonode.s(
            hazard_layer_uri
        ).set(queue=push_to_geonode.queue),

        # Handle the push result
        handle_push_to_geonode.s(
            hazard_class,
            hazard_event_id
        )
    )

    @app.task
    def _handle_error(req, exc, traceback):
        """Update task status as Failure."""
        hazard_event.push_task_status = 'FAILURE'

    async_result = tasks_chain.apply_async()
    hazard_event.push_task_status = async_result.state
