"""myEWB networks views

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Last modified on 2009-08-06
@author Joshua Gorner, Benjamin Best
"""

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User

from networks.models import Network
from networks.forms import NetworkForm

from base_groups.views import *
from base_groups.views import members
from base_groups.models import BaseGroup, GroupMember, GroupLocation
from base_groups.forms import GroupMemberForm, GroupLocationForm
from base_groups.helpers import *

INDEX_TEMPLATE = 'networks/networks_index.html'
NEW_TEMPLATE = 'networks/new_network.html'
EDIT_TEMPLATE = 'networks/edit_network.html'
DETAIL_TEMPLATE = 'networks/network_detail.html'
ADMIN_TEMPLATE = 'networks/admin.html'

LOCATION_TEMPLATE = 'networks/edit_network_location.html'

MEM_INDEX_TEMPLATE = 'networks/members_index.html'
MEM_NEW_TEMPLATE = 'networks/new_member.html'
MEM_EDIT_TEMPLATE = 'networks/edit_member.html'
MEM_DETAIL_TEMPLATE = 'networks/member_detail.html'


DEFAULT_OPTIONS = {"check_create": True}

def networks_index(request, form_class=NetworkForm, template_name=INDEX_TEMPLATE,
        new_template_name=NEW_TEMPLATE):
    return groups_index(request, Network, GroupMember, form_class, template_name, new_template_name, DEFAULT_OPTIONS)

@permission_required('networks.add')
def new_network(request, form_class=NetworkForm, template_name=NEW_TEMPLATE, 
        index_template_name=INDEX_TEMPLATE):
    return new_group(request, Network, GroupMember, form_class, template_name, index_template_name, DEFAULT_OPTIONS)

def network_detail(request, group_slug, form_class=NetworkForm, template_name=DETAIL_TEMPLATE,
        edit_template_name=EDIT_TEMPLATE):
    return group_detail(request, group_slug, Network, GroupMember, form_class, template_name, edit_template_name, DEFAULT_OPTIONS)

@permission_required('networks.change')
def edit_network(request, group_slug, form_class=NetworkForm, template_name=EDIT_TEMPLATE,
        detail_template_name=DETAIL_TEMPLATE):
    return edit_group(request, group_slug, Network, GroupMember, form_class, template_name, detail_template_name, DEFAULT_OPTIONS)

@permission_required('networks.delete')
def delete_network(request, group_slug, form_class=NetworkForm, detail_template_name=DETAIL_TEMPLATE):
    return delete_group(request, group_slug, Network, GroupMember, form_class, detail_template_name, DEFAULT_OPTIONS)

# IS there  a permission for this? Are these permissions redundant anyways?
def network_admin_page(request, group_slug, template_name=ADMIN_TEMPLATE):
    return group_admin_page(request, group_slug, Network, template_name)
            
@permission_required('networks.change')
def edit_network_location(request, group_slug, form_class=GroupLocationForm, template_name=LOCATION_TEMPLATE):
    return edit_group_location(request, group_slug, Network, form_class, template_name, DEFAULT_OPTIONS)
    
        
def members_index(request, group_slug, form_class=GroupMemberForm, template_name=MEM_INDEX_TEMPLATE, 
        new_template_name=MEM_NEW_TEMPLATE):
    return members.members_index(request, group_slug, Network, form_class, template_name, new_template_name)
    
@login_required
def new_member(request, group_slug, form_class=GroupMemberForm, template_name=MEM_NEW_TEMPLATE,
        index_template_name=MEM_INDEX_TEMPLATE):
    return members.new_member(request, group_slug, Network, form_class, template_name, index_template_name)
    
def member_detail(request, group_slug, username, form_class=GroupMemberForm, template_name=MEM_DETAIL_TEMPLATE,
        edit_template_name=MEM_EDIT_TEMPLATE):
    return members.member_detail(request, group_slug, username, Network, form_class, template_name, edit_template_name)

@login_required
def edit_member(request, group_slug, username, form_class=GroupMemberForm, template_name=MEM_EDIT_TEMPLATE,
        detail_template_name=MEM_DETAIL_TEMPLATE):
    return members.edit_member(request, group_slug, username, Network, form_class, template_name, detail_template_name)

@login_required    
def delete_member(request, group_slug, username):
    return members.delete_member(request, group_slug, username, Network)

def ajax_search(request, network_type):
    search_term = request.GET.get('q', '')
    networks = []
    
    if search_term:
        # TODO: implement public/private visibility
        networks = Network.objects.all()
        networks = networks.filter(name__icontains=search_term)
        networks = networks.filter(network_type__iexact=network_type)
        networks = networks.order_by("name")
    
    return render_to_response('networks/ajax_search.html', {
        "networks": networks        
    }, context_instance=RequestContext(request))
    
