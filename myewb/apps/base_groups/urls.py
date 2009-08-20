"""myEWB base groups URLs

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Last modified on 2009-07-29
@author Joshua Gorner
"""

from django.conf.urls.defaults import *

from base_groups.models import BaseGroup

from groups.bridge import ContentBridge


bridge = ContentBridge(BaseGroup, 'groups')

urlpatterns = patterns('base_groups.views',    
    # Modified REST - only GET and POST used

    # GET - groups index
    # POST - create group
    url(r'^$', 'groups_index', name='groups_index',),
    # GET - new group form
    # POST - create group (redirects to 'groups_index'
    # url(r'^new/$', 'new_group', name='new_group',),

    # GET - retrieve group detail
    # POST - update group
    url(r'^(?P<group_slug>[-\w]+)/$', 'group_detail', name='group_detail',),
    # GET - edit group form
    # POST - update group (redirects to 'group_detail'
    url(r'^(?P<group_slug>[-\w]+)/edit/$', 'edit_group', name='edit_group',),
    # POST - delete group
    url(r'^(?P<group_slug>[-\w]+)/delete/$', 'delete_group', name='delete_group',),
)

urlpatterns += patterns('base_groups.views.members', 
    # Modified REST - only GET and POST used

    # GET - members index
    # POST - create member
    url(r'^(?P<group_slug>[-\w]+)/members/$', 'members_index', name='members_index',),
    # GET - new member form
    # POST - create member (redirects to 'members_index'
    url(r'^(?P<group_slug>[-\w]+)/members/new/$', 'new_member', name='new_member',),

    # GET - retrieve member detail
    # POST - update member
    url(r'^(?P<group_slug>[-\w]+)/members/(?P<username>[\w\._-]+)/$', 'member_detail', name='member_detail',),
    # GET - edit member form
    # POST - update member (redirects to 'member_detail'
    url(r'^(?P<group_slug>[-\w]+)/members/(?P<username>[\w\._-]+)/edit/$', 'edit_member', name='edit_member',),
    # POST - delete member
    url(r'^(?P<group_slug>[-\w]+)/members/(?P<username>[\w\._-]+)/delete/$', 'delete_member', name='delete_member',),
)

urlpatterns += bridge.include_urls('group_topics.urls.groups', r'^(?P<group_slug>[-\w]+)/posts/')