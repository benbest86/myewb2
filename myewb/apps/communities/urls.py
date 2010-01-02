"""myEWB communities URLs

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Last modified on 2009-08-07
@author Joshua Gorner
"""

from django.conf.urls.defaults import *

from communities.models import Community

from groups.bridge import ContentBridge
from base_groups.helpers import group_url_patterns

#bridge = ContentBridge(Community, 'communities')
bridge = ContentBridge(Community, Community._meta.verbose_name)

urlpatterns = group_url_patterns(Community)    
urlpatterns += bridge.include_urls('group_topics.urls.groups', r'^(?P<group_slug>[-\w]+)/posts/')
urlpatterns += bridge.include_urls('whiteboard.urls', r'^(?P<group_slug>[-\w]+)/whiteboard/')
