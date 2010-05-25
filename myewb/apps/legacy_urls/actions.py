from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse

urlpatterns = patterns('django.views.generic.simple',
    url(r'^ModifyListMembership/(?P<group_id>\d+)$', 'redirect_to', {'url': reverse('topic_feed_all'),
                                    'permanent': True}),
    )