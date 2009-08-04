"""myEWB networks URLs

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Last modified on 2009-07-29
@author Joshua Gorner
"""

from django.conf.urls.defaults import *

from networks.models import Network

from groups.bridge import ContentBridge


bridge = ContentBridge(Network, 'networks')

urlpatterns = patterns('networks.views',    
    # Modified REST - only GET and POST used

    # GET - networks index
    # POST - create network
    url(r'^$', 'networks_index', name='networks_index',),
    # GET - new network form
    # POST - create network (redirects to 'networks_index'
    url(r'^new/$', 'new_network', name='new_network',),
    
    # GET - ajax list of matching groups
    url(r'^ajax/(?P<network_type>[-\w]+)/$', 'ajax_search', name='ajax_search_network',),
    
    # GET - retrieve network detail
    # POST - update network
    url(r'^(?P<group_slug>[-\w]+)/$', 'network_detail', name='network_detail',),
    # GET - edit network form
    # POST - update network (redirects to 'network_detail'
    url(r'^(?P<group_slug>[-\w]+)/edit/$', 'edit_network', name='edit_network',),
    # POST - delete network
    url(r'^(?P<group_slug>[-\w]+)/delete/$', 'delete_network', name='delete_network',),
    
    # edit network location
    url(r'^(?P<group_slug>[-\w]+)/location/$', 'edit_network_location', name='edit_network_location',),
    
    # GET - members index
    # POST - create member
    url(r'^(?P<group_slug>[-\w]+)/members/$', 'members_index', name='network_members_index',),
    # GET - new member form
    # POST - create member (redirects to 'members_index'
    url(r'^(?P<group_slug>[-\w]+)/members/new/$', 'new_member', name='network_new_member',),

    # GET - retrieve member detail
    # POST - update member
    url(r'^(?P<group_slug>[-\w]+)/members/(?P<username>[\w\._-]+)/$', 'member_detail', name='network_member_detail',),
    # GET - edit member form
    # POST - update member (redirects to 'member_detail'
    url(r'^(?P<group_slug>[-\w]+)/members/(?P<username>[\w\._-]+)/edit/$', 'edit_member', name='network_edit_member',),
    # POST - delete member
    url(r'^(?P<group_slug>[-\w]+)/members/(?P<username>[\w\._-]+)/delete/$', 'delete_member', name='network_delete_member',),
)

urlpatterns += bridge.include_urls('topics.urls', r'^(?P<group_slug>[-\w]+)/topics/')
