from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse

urlpatterns = patterns('django.views.generic.simple',
    url(r'^posts/Any$', 'redirect_to', {'url': reverse('topic_feed_all'),
                                    'permanent': True}),
    url(r'^posts/Any plus Replies$', 'redirect_to', {'url': reverse('topic_feed_all'),
                                    'permanent': True}),
    url(r'^posts/(?P<tag>[-\w]+)$', 'redirect_to', {'url': '/feeds/posts/tag/%(tag)s/',
                                    'permanent': True}),
    url(r'^hot/Any$', 'redirect_to', {'url': reverse('topic_feed_featured'),
                                    'permanent': True}),
    url(r'^hot/Any plus Replies$', 'redirect_to', {'url': reverse('topic_feed_featured'),
                                    'permanent': True}),
    url(r'^list/(?P<group_slug>[-\w]+)$', 'redirect_to', {'url': '/feeds/posts/group/%(group_slug)s/',
                                    'permanent': True}),
    url(r'^calendar/(?P<group_slug>[-\w]+).ics$', 'redirect_to', {'url': '/events/ical/for/networks/network/slug/%(group_slug)s/',
                                    'permanent': True}),
    )