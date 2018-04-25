# coding=utf-8
from django.contrib.auth.decorators import permission_required
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import redirect

from realtime.models.coreflatpage import CoreFlatPage


@permission_required(
    perm=[
        'realtime.add_coreflatpage',
        'realtime.change_coreflatpage',
    ],
    login_url=reverse_lazy('realtime_admin:login'))
def edit(request, slug_id, system_category, language):
    """Mainly used to redirect internal CMS urls."""
    try:
        page = CoreFlatPage.objects.get(
            slug_id=slug_id,
            system_category=system_category,
            language=language)
    except CoreFlatPage.DoesNotExist:
        page = CoreFlatPage.objects.create(
            slug_id=slug_id,
            system_category=system_category,
            language=language)
        page.url = '/{system_category}/{slug_id}/{language}/'.format(
            system_category=system_category,
            slug_id=slug_id,
            language=language)
        site = Site.objects.first()
        page.sites.add(site)
        page.group = system_category
        page.save()

    return redirect(
        reverse('admin:realtime_coreflatpage_change', args=(page.id, )))
