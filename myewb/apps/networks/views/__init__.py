"""myEWB networks views

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Last modified on 2009-08-06
@author Joshua Gorner, Benjamin Best
"""

import string
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from emailconfirmation.models import EmailAddress

from networks.models import Network
from networks.forms import NetworkForm, NetworkBulkImportForm, NetworkUnsubscribeForm
from siteutils.helpers import get_email_user

from base_groups.views import *
from base_groups.views import members
from base_groups.models import BaseGroup, GroupMember, GroupLocation
from base_groups.forms import GroupMemberForm, GroupLocationForm
from base_groups.helpers import *
from base_groups.decorators import group_admin_required

INDEX_TEMPLATE = 'networks/networks_index.html'
NEW_TEMPLATE = 'networks/new_network.html'
EDIT_TEMPLATE = 'networks/edit_network.html'
DETAIL_TEMPLATE = 'networks/network_detail.html'

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
    
@group_admin_required()
def bulk_import(request, group_slug, form_class=NetworkBulkImportForm, template_name='networks/bulk_import.html'):
    group = get_object_or_404(Network, slug=group_slug)
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            raw_emails = form.cleaned_data['emails']
            emails = raw_emails.split()   # splits by whitespace characters
            
            for email in emails:
                email_user = get_email_user(email)
                if email_user is None:
                    username = User.objects.make_random_password()     # not a password per se, just a random string
                    while User.objects.filter(username=username).count() > 0:   # ensure uniqueness
                        username = User.objects.make_random_password()
                    email_user = User.objects.create_user(username, email)      # sets "unusable" password
                    email_user.save()
                
                existing_members = GroupMember.objects.filter(group=group, user=email_user)
                if existing_members.count() == 0:              
                    # set the request_status according to the existence of the user.
                    # users with a password are real and get 'A', users without are
                    # bulk users and get 'B'
                    request_status = email_user.has_usable_password() and 'A' or 'B'
                    nm = GroupMember(group=group, user=email_user, request_status=request_status)
                    nm.save()
            # redirect to network home page on success
            return HttpResponseRedirect(reverse('network_detail', kwargs={'group_slug': group.slug}))
    else:
        form = form_class()
    return render_to_response(template_name, {
        "group": group,
        "form": form,
    }, context_instance=RequestContext(request))

def unsubscribe(request, form_class=NetworkUnsubscribeForm, template_name='networks/unsubscribe.html'):
    if request.method == 'POST':
        form = form_class(request.POST)
        message = None
        if form.is_valid():
            email = form.cleaned_data['email']            
            email_user = get_email_user(email)
            
            if email_user and not email_user.has_usable_password():
                email_user.delete()
                message = _("The email address has been successfully removed from our mailing lists.")
            else:
                message = _("The email address you entered is not listed in our records as a mailing list recipient. Please ensure you entered the address correctly, or enter another email address.")
    
    form = form_class()
    return render_to_response(template_name, {
        "form": form,
        "message": message,
    }, context_instance=RequestContext(request))
