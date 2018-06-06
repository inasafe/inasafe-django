# coding=utf-8
"""InaSAFE Django task related to GeoNode upload."""
from __future__ import absolute_import

from core.celery_app import app

from realtime.models.ash import Ash
from realtime.tasks.headless.inasafe_wrapper import push_to_geonode

GEONODE_PUSH_SUCCESS = 0

@app.task(queue='inasafe-django')
def upload_layer_to_geonode(process_result, event_id):
    """Upload layer to geonode."""
    hazard = Ash.objects.get(id=event_id)
    hazard_layer_uri = hazard.hazard_path
    return push_to_geonode(hazard_layer_uri)

@app.task(queue='inasafe-django')
def handle_push_to_geonode(push_result, event_id):
    """Handle geonode push result."""
    # TODO(IS): make it generic for all hazard, somehow
    hazard = Ash.objects.get(id=event_id)
    task_state = 'FAILURE'
    if not push_result:
        task_state = 'FAILURE'
    elif push_result['status'] == GEONODE_PUSH_SUCCESS:
        task_state = 'SUCCESS'
    hazard.push_task_status = task_state
    hazard.push_task_result = push_result
    hazard.save()
