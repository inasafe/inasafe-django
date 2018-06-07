# coding=utf-8
"""InaSAFE Django task related to GeoNode upload."""
from __future__ import absolute_import
import logging

from celery import chain

from core.celery_app import app

from realtime.models.ash import Ash
from realtime.models.flood import Flood
from realtime.models.earthquake import Earthquake
from realtime.app_settings import LOGGER_NAME
from realtime.tasks.headless.inasafe_wrapper import push_to_geonode

LOGGER = logging.getLogger(LOGGER_NAME)
GEONODE_PUSH_SUCCESS = 0


@app.task(queue='inasafe-django')
def handle_push_to_geonode(push_result, hazard_class_name, hazard_event_id):
    """Handle geonode push result."""
    hazard_class_mapping = {
        Ash.__name__: Ash,
        Flood.__name__: Flood,
        Earthquake.__name__: Earthquake
    }

    # Hacky thing to get proper class
    if hazard_class_name not in hazard_class_mapping.keys():
        for key in hazard_class_mapping.keys():
            if key.lower() in hazard_class_name.lower():
                hazard_class_name = key
                break
    hazard_class = hazard_class_mapping.get(hazard_class_name)
    task_state = 'FAILURE'
    if not push_result:
        task_state = 'FAILURE'
    elif push_result['status'] == GEONODE_PUSH_SUCCESS:
        task_state = 'SUCCESS'

    # Use update so it doesn't trigger save signal
    hazard_class.objects.filter(id=hazard_event_id).update(
        push_task_status=task_state,
        push_task_result=push_result
    )


@app.task(queue='inasafe-django')
def push_hazard_to_geonode(hazard_event):
    """Upload layer to geonode and update the status of hazard."""
    LOGGER.info('Push layer to geonode.')
    # Skip if it's already running
    if hazard_event.push_task_status:
        return
    hazard_layer_uri = hazard_event.hazard_path
    hazard_event_id = hazard_event.id
    hazard_class = hazard_event.__class__
    hazard_class_name = hazard_class.__name__

    tasks_chain = chain(
        # Push to layer to geonode
        push_to_geonode.s(
            hazard_layer_uri
        ).set(queue=push_to_geonode.queue),

        # Handle the push result
        handle_push_to_geonode.s(
            hazard_class_name,
            hazard_event_id
        ).set(queue=handle_push_to_geonode.queue)
    )

    @app.task
    def _handle_error(req, exc, traceback):
        """Update task status as Failure."""
        hazard_event.push_task_status = 'FAILURE'

    async_result = tasks_chain.apply_async()
    hazard_event.push_task_status = async_result.state
