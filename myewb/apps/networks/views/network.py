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
from networks.forms import NetworkForm, NetworkBulkImportForm, NetworkUnsubscribeForm, NetworkMemberForm, EditNetworkMemberForm
from siteutils.helpers import get_email_user

from base_groups.views import *
from base_groups.views import members
from base_groups.models import BaseGroup, GroupMember, GroupLocation
from base_groups.forms import GroupMemberForm, GroupInviteForm, EditGroupMemberForm, GroupLocationForm
from base_groups.helpers import *
from base_groups.decorators import group_admin_required
from communities.models import NationalRepList, ExecList

INDEX_TEMPLATE = 'networks/networks_index.html'
NEW_TEMPLATE = 'networks/new_network.html'
EDIT_TEMPLATE = 'networks/edit_network.html'
DETAIL_TEMPLATE = 'networks/network_detail.html'
CHAPTER_TEMPLATE = 'networks/chapter_detail.html'

LOCATION_TEMPLATE = 'networks/edit_network_location.html'

MEM_INDEX_TEMPLATE = 'networks/members_index.html'
MEM_NEW_TEMPLATE = 'networks/new_member.html'
MEM_INVITE_TEMPLATE = 'networks/invite_member.html'
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
    network = get_object_or_404(Network, slug=group_slug)
    return group_detail(request, group_slug, Network, GroupMember, form_class, template_name, edit_template_name, DEFAULT_OPTIONS)

@group_admin_required()
def edit_network(request, group_slug, form_class=NetworkForm, template_name=EDIT_TEMPLATE,
        detail_template_name=DETAIL_TEMPLATE):
    return edit_group(request, group_slug, Network, GroupMember, form_class, template_name, detail_template_name, DEFAULT_OPTIONS)

@permission_required('networks.delete')
def delete_network(request, group_slug, form_class=NetworkForm, detail_template_name=DETAIL_TEMPLATE):
    return delete_group(request, group_slug, Network, GroupMember, form_class, detail_template_name, DEFAULT_OPTIONS)
            
@group_admin_required()
def edit_network_location(request, group_slug, form_class=GroupLocationForm, template_name=LOCATION_TEMPLATE):
    return edit_group_location(request, group_slug, Network, form_class, template_name, DEFAULT_OPTIONS)
    
        
def members_index(request, group_slug, form_class=GroupMemberForm, template_name=MEM_INDEX_TEMPLATE, 
        new_template_name=MEM_NEW_TEMPLATE):
    return members.members_index(request, group_slug, Network, form_class, template_name, new_template_name)
    
@login_required
def new_member(request, group_slug, form_class=NetworkMemberForm, template_name=MEM_NEW_TEMPLATE,
        index_template_name=MEM_INDEX_TEMPLATE, force_join=False):

    validated = update_magic_lists(request, group_slug, None, form_class)
        
    if validated:
        return members.new_member(request, group_slug, Network, form_class, template_name, index_template_name, force_join)
    else:
        request.user.message_set.create(message='User is already an exec of another chapter!')
        return HttpResponseRedirect(reverse('network_members_index', kwargs={'group_slug': group_slug}))
    
@login_required
def invite_member(request, group_slug, form_class=GroupInviteForm, template_name=MEM_INVITE_TEMPLATE,
        index_template_name=MEM_INDEX_TEMPLATE):
    return members.invite_member(request, group_slug, Network, form_class, template_name, index_template_name)
    
def member_detail(request, group_slug, username, form_class=EditGroupMemberForm, template_name=MEM_DETAIL_TEMPLATE,
        edit_template_name=MEM_EDIT_TEMPLATE):
    return members.member_detail(request, group_slug, username, Network, form_class, template_name, edit_template_name)

@login_required
def edit_member(request, group_slug, username, form_class=EditNetworkMemberForm, template_name=MEM_EDIT_TEMPLATE,
        detail_template_name=MEM_DETAIL_TEMPLATE):
    
    validated = update_magic_lists(request, group_slug, username, form_class)
        
    if validated:
        return members.edit_member(request, group_slug, username, Network, form_class, template_name, detail_template_name)
    else:
        request.user.message_set.create(message='User is already an exec of another chapter!')
        return HttpResponseRedirect(reverse('network_members_index', kwargs={'group_slug': group_slug}))

@login_required    
def delete_member(request, group_slug, username):
    return members.delete_member(request, group_slug, username, Network)

@group_admin_required()
def network_stats(request, group_slug):
    return stats(request, group_slug, Network, "networks/stats.html")

def ajax_search(request, network_type):
    search_term = request.GET.get('q', '')
    networks = []
    
    if search_term:
        # TODO: implement public/private visibility
        networks = Network.objects.all()
        networks = networks.filter(is_active=True)
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
                group.add_email(email)

            # redirect to network home page on success
            return HttpResponseRedirect(reverse('network_detail', kwargs={'group_slug': group.slug}))
    else:
        form = form_class()
    return render_to_response(template_name, {
        "group": group,
        "form": form,
    }, context_instance=RequestContext(request))
    
@group_admin_required()
def bulk_remove(request, group_slug, form_class=NetworkBulkImportForm, template_name='networks/bulk_remove.html'):
    group = get_object_or_404(Network, slug=group_slug)
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            raw_emails = form.cleaned_data['emails']
            emails = raw_emails.split()   # splits by whitespace characters
            
            for email in emails:
                email_user = get_email_user(email)
                if email_user is not None:
                    group.remove_member(email_user)
            return HttpResponseRedirect(reverse('network_detail', kwargs={'group_slug': group.slug}))
    else:
        form = form_class()
    return render_to_response(template_name, {
        "group": group,
        "form": form,
    }, context_instance=RequestContext(request))
    
def unsubscribe(request, form_class=NetworkUnsubscribeForm, template_name='networks/unsubscribe.html'):
    message = None

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']            
            email_user = get_email_user(email)
            
            if email_user:
                if email_user.is_bulk:
                    email_user.softdelete()
                    message = _("The email address has been successfully removed from our mailing lists.")
                else:
                    message = _("The email address is associated with a myEWB account - you must sign in to delete your account..")
            else:
                message = _("The email address you entered is not listed in our records as a mailing list recipient. Please ensure you entered the address correctly, or enter another email address.")
    else:
        form = form_class()
        
    return render_to_response(template_name, {
        "form": form,
        "message": message,
    }, context_instance=RequestContext(request))
    
# bit of a hack to display a national office listing... basically, all admins
# of a hard-coded network.
def national_office(request):
    # could probably do this with a template shortcut instead?
    
    try:
        group = Network.objects.get(slug="natloffice")
    except:
        group = None
    
    return render_to_response("networks/national_office.html", {
        "group": group
    }, context_instance=RequestContext(request))
    
    
def update_magic_lists(request, group_slug, username, form_class):

    if request.method == 'POST':
        # grab basic objects
        group = get_object_or_404(Network, slug=group_slug)
        user = request.user

        if username:
            other_user = get_object_or_404(User, username=username)
            member = get_object_or_404(GroupMember, group=group, user=other_user)
            users = [other_user]
            form = form_class(request.POST, instance=member)
        else:
            users = None
            form = form_class(request.POST)

        # saving the object
        if form.is_valid():
            if not users:
                users = form.cleaned_data['user']
                
            for other_user in users:
                # find the current membership status with this group
                try:
                    member = GroupMember.objects.get(group=group, user=other_user)
                except GroupMember.DoesNotExist:
                    member = None
                
                # Start with exec lists...
                if form.cleaned_data['is_admin'] == True:
                    if group.is_chapter():
                        # see if they are on a different chapter's exec list:
                        # parent__isnull=False ensures it's a chapter list (not a global list)
                        # member_users=other_user membership check
                        # and the exclusion ensures it's a different chapter's list
                        otherexec = ExecList.objects.filter(parent__isnull=False,
                                                            member_users=other_user,
                                                            is_active=True)
                        otherexec = otherexec.exclude(parent=group)
                        
                        if otherexec.count() > 0:
                            # if they are on a different chapter's list,
                            # don't let them be added here!!!
                            return False
                        
                        
                        # TODO: don't hard-code slug?
                        try:    # all execs
                            allexec = ExecList.objects.get(slug='exec')
                            allexec.add_member(other_user)
                        except:
                            pass
                        
                        try:    # chapter-specific execs
                            chapterexec = ExecList.objects.get(parent=group)
                            chapterexec.add_member(other_user)
                        except:
                            pass
                        
                        if group.chapter_info.student:
                            # TODO: don't hard-code slug?
                            try:
                                stuexec = ExecList.objects.get(slug='unichaptersexec')
                                stuexec.add_member(other_user)
                            except:
                                pass
                        else:
                            # TODO: don't hard-code slug?
                            try:
                                proexec = ExecList.objects.get(slug='prochaptersexec')
                                proexec.add_member(other_user)
                            except:
                                pass

                # remove from exec lists if no longer exec                                
                # the check for member and member.is_admin ensures that this
                # code is only run if they have been downgraded from this
                # chapter's exec (not being added to a different chapter's regular list)
                elif member and member.is_admin:
                    execlists = ExecList.objects.filter(member_users=other_user, is_active=True)
                    for list in execlists:
                        list.remove_member(other_user)

                # build list of Natl Rep objects that user should be in
                currentlists = NationalRepList.objects.filter(member_users=other_user, is_active=True)
                newlists = []
                
                if form.cleaned_data['is_admin'] == True:
                    selected_lists = form.cleaned_data['replists']
                elif member and member.is_admin:
                    # same check as earlier
                    selected_lists = []
                else:
                    selected_lists = None
                    
                if selected_lists is not None:
                    for listslug in selected_lists:
                        list = get_object_or_404(NationalRepList, slug=listslug)
                        newlists.append(list)
                    
                        # add to list if not already on it
                        if list not in currentlists:
                            obj = list.add_member(other_user)
                    
                    # get current lists, remove from rep lists as needed
                    for list in currentlists:
                        if list not in newlists:
                            list.remove_member(other_user)
                        
    return True