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

urlpatterns = patterns('base_groups.views.groups',    
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
    url(r'^id/(?P<group_id>\d+)/$', 'group_detail_by_id', name='group_detail_by_id',),

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
    url(r'^(?P<group_slug>[-\w]+)/members/new/join/$', 'new_member', kwargs={'force_join': True}, name='new_member',),

    url(r'^(?P<group_slug>[-\w]+)/members/new/email$', 'new_email_member', name='new_email_member',),
    url(r'^(?P<group_slug>[-\w]+)/members/export/$', 'members_csv', name='group_member_export',),

    # GET - retrieve member detail
    # POST - update member
    url(r'^(?P<group_slug>[-\w]+)/members/(?P<username>[\w\._-]+)/$', 'member_detail', name='member_detail',),
    # GET - edit member form
    # POST - update member (redirects to 'member_detail'
    url(r'^(?P<group_slug>[-\w]+)/members/(?P<username>[\w\._-]+)/edit/$', 'edit_member', name='edit_member',),
    # POST - delete member
    url(r'^(?P<group_slug>[-\w]+)/members/(?P<username>[\w\._-]+)/delete/$', 'delete_member', name='delete_member',),
)

urlpatterns += patterns('base_groups.views.workspace',
    url(r'(?P<group_slug>[-\w]+)/workspace/browse/$', 'browse', name='group_workspace_browse'),
    url(r'(?P<group_slug>[-\w]+)/workspace/detail/$', 'detail', name='group_workspace_detail'),
    url(r'(?P<group_slug>[-\w]+)/workspace/upload/$', 'upload', name='group_workspace_upload'),
    url(r'(?P<group_slug>[-\w]+)/workspace/move/$', 'move', name='group_workspace_move'),
    url(r'(?P<group_slug>[-\w]+)/workspace/replace/$', 'replace', name='group_workspace_replace'),
    url(r'(?P<group_slug>[-\w]+)/workspace/delete/$', 'delete', name='group_workspace_delete')
) 

urlpatterns += bridge.include_urls('whiteboard.urls', r'^(?P<group_slug>[-\w]+)/whiteboard/')
urlpatterns += bridge.include_urls('group_topics.urls.groups', r'^(?P<group_slug>[-\w]+)/posts/')
