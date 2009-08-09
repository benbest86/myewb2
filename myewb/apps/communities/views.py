"""myEWB communities views

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Created on 2009-08-06
Last modified on 2009-08-07
@author Joshua Gorner, Benjamin Best
"""

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User

from communities.models import Community, CommunityMember
from communities.forms import CommunityForm, CommunityMemberForm

from base_groups.views import *
from base_groups.views import members
from base_groups.models import BaseGroup, GroupMember, GroupLocation
from base_groups.forms import GroupLocationForm
from base_groups.helpers import *

INDEX_TEMPLATE = 'communities/communities_index.html'
NEW_TEMPLATE = 'communities/new_community.html'
EDIT_TEMPLATE = 'communities/edit_community.html'
DETAIL_TEMPLATE = 'communities/community_detail.html'

LOCATION_TEMPLATE = 'communities/edit_community_location.html'

MEM_INDEX_TEMPLATE = 'communities/members_index.html'
MEM_NEW_TEMPLATE = 'communities/new_member.html'
MEM_EDIT_TEMPLATE = 'communities/edit_member.html'
MEM_DETAIL_TEMPLATE = 'communities/member_detail.html'

DEFAULT_OPTIONS = {}


def communities_index(request, form_class=CommunityForm, template_name=INDEX_TEMPLATE,
        new_template_name=NEW_TEMPLATE):
    return groups_index(request, Community, CommunityMember, form_class, template_name, new_template_name, DEFAULT_OPTIONS)

@login_required
def new_community(request, form_class=CommunityForm, template_name=NEW_TEMPLATE, 
        index_template_name=INDEX_TEMPLATE):
    return new_group(request, Community, CommunityMember, form_class, template_name, index_template_name, DEFAULT_OPTIONS)

def community_detail(request, group_slug, form_class=CommunityForm, template_name=DETAIL_TEMPLATE,
        edit_template_name=EDIT_TEMPLATE):
    return group_detail(request, group_slug, Community, CommunityMember, form_class, template_name, edit_template_name, DEFAULT_OPTIONS)

@login_required
def edit_community(request, group_slug, form_class=CommunityForm, template_name=EDIT_TEMPLATE,
        detail_template_name=DETAIL_TEMPLATE):
    return edit_group(request, group_slug, Community, CommunityMember, form_class, template_name, detail_template_name, DEFAULT_OPTIONS)

@login_required
def delete_community(request, group_slug, form_class=CommunityForm, detail_template_name=DETAIL_TEMPLATE):
    return delete_group(request, group_slug, Community, CommunityMember, form_class, detail_template_name, DEFAULT_OPTIONS)
    
        
def members_index(request, group_slug, form_class=CommunityMemberForm, template_name=MEM_INDEX_TEMPLATE, 
        new_template_name=MEM_NEW_TEMPLATE):
    return members.members_index(request, group_slug, Community, form_class, template_name, new_template_name)
    
@login_required
def new_member(request, group_slug, form_class=CommunityMemberForm, template_name=MEM_NEW_TEMPLATE,
        index_template_name=MEM_INDEX_TEMPLATE):
    return members.new_member(request, group_slug, Community, form_class, template_name, index_template_name)
    
def member_detail(request, group_slug, username, form_class=CommunityMemberForm, template_name=MEM_DETAIL_TEMPLATE,
        edit_template_name=MEM_EDIT_TEMPLATE):
    return members.member_detail(request, group_slug, username, Community, form_class, template_name, edit_template_name)

@login_required
def edit_member(request, group_slug, username, form_class=CommunityMemberForm, template_name=MEM_EDIT_TEMPLATE,
        detail_template_name=MEM_DETAIL_TEMPLATE):
    return members.edit_member(request, group_slug, username, Community, form_class, template_name, detail_template_name)

@login_required    
def delete_member(request, group_slug, username):
    return members.delete_member(request, group_slug, username, Community)
