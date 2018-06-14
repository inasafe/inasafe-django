# -*- coding: utf-8 -*-
import logging

from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.conf import settings

LOG = logging.getLogger(__name__)


class MainView(TemplateView):
    template_name = 'main.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['debug'] = settings.DEBUG
        return context

    def get(self, request, *args, **kwargs):
        return redirect('/realtime/')


class AboutView(TemplateView):
    template_name = 'about.html'


class HelpView(TemplateView):
    template_name = 'help.html'
