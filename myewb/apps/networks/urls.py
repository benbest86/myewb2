"""myEWB networks URLs

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Last modified on 2009-08-06
@author Joshua Gorner
"""

from django.conf.urls.defaults import *

from networks.models import Network

from groups.bridge import ContentBridge
from base_groups.helpers import group_url_patterns

bridge = ContentBridge(Network, 'networks')

urlpatterns = group_url_patterns(Network, url(r'^ajax/(?P<network_type>[-\w]+)/$', 'ajax_search', name='ajax_search_network',))

urlpatterns += patterns('networks.views', 
    url(r'^(?P<group_slug>[-\w]+)/new/$', 'new_member', name='new_network_member'),
    url(r'^(?P<group_slug>[-\w]+)/(?P<username>\w+)/delete/$', 'delete_member', name='delete_network_member'),
    url(r'^(?P<group_slug>[-\w]+)/location/$', 'edit_network_location', name='edit_network_location',),
)
    
urlpatterns += bridge.include_urls('topics.urls', r'^(?P<group_slug>[-\w]+)/topics/')
