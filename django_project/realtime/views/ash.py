# coding=utf-8

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from realtime.forms import AshUploadForm

__author__ = 'ismailsunni'
__project_name__ = 'inasafe-django'
__filename__ = 'ash'
__date__ = '7/15/16'
__copyright__ = 'imajimatika@gmail.com'


def index(request):
    """Upload ash event."""
    if request.method == 'POST':
        form = AshUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('realtime:ash_index'))
    else:
        form = AshUploadForm()  # A empty, unbound form

    # Render the form
    return render_to_response(
        'realtime/ash/index.html',
        {'form': form},
        context_instance=RequestContext(request)
    )
