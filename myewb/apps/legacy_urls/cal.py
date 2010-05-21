from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse

urlpatterns = patterns('django.views.generic.simple',

    url(r'^chapterical/(?P<group_slug>[-\w]+).ics$', 'redirect_to', {'url': '/events/ical/for/networks/network/slug/%(group_slug)s/',
                                    'permanent': True}),
    )
