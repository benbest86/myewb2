from django.conf.urls.defaults import *

from networks.models import Network
from communities.models import Community

from groups.bridge import ContentBridge

networks_bridge = ContentBridge(Network, 'networks')
communities_bridge = ContentBridge(Community, 'communities')

urlpatterns = networks_bridge.include_urls('ideas_app.plugin_urls', r'^networks/(?P<group_slug>[-\w]+)/ideas/')
urlpatterns += communities_bridge.include_urls('ideas_app.plugin_urls', r'^communities/(?P<group_slug>[-\w]+)/ideas/')
urlpatterns += patterns('ideas_app.views',
        url(r'^ideas_app/preferences/(?P<group_slug>[-\w]+)/$', 'ideas_app_preference', name='ideas_app_preference'),
)
