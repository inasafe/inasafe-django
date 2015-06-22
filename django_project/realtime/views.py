# coding=utf-8
"""Views of the apps."""
from django.shortcuts import render, render_to_response
from realtime.forms import FilterForm
from realtime.models.earthquake import Earthquake
from django.template import RequestContext, loader
from user_map.app_settings import LEAFLET_TILES
from django.http import HttpResponse, Http404


def index(request):
    """Index page of user map.

    :param request: A django request object.
    :type request: request

    :returns: Response will be a leaflet map page.
    :rtype: HttpResponse
    """

    if request.method == 'POST':
        pass
    else:
        form = FilterForm()

    leaflet_tiles = dict(
        url=LEAFLET_TILES[1],
        attribution=LEAFLET_TILES[2]
        )

    context = RequestContext(request)
    context['leaflet_tiles'] = leaflet_tiles
    return render_to_response(
            'realtime/index.html',
            {'form': form},
            context_instance=context
            )


def get_earthquakes(request):
    """Return a json document of earthquakes of the project.
    :param request: A django request object.
    :type request: request
    """
    if request.method == 'GET':

        # Get data:
        events = Earthquake.objects.all()
        context = {'events': events}
        events_json = loader.render_to_string(
            'realtime/events.json',
            context_instance=RequestContext(request, context))
        # Return Response
        return HttpResponse(events_json, content_type='application/json')
    else:
        raise Http404
