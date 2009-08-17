"""myEWB base groups generic views

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Last modified on 2009-08-02
@author Joshua Gorner, Benjamin Best
"""

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from base_groups.models import BaseGroup, GroupMember
from base_groups.forms import GroupMemberForm
from base_groups.decorators import own_member_object_required, group_admin_required, visibility_required

@visibility_required()
def members_index(request, group_slug, group_model=None, form_class=None, template_name=None, new_template_name=None):
    # handle generic call
    if group_model is None and request.method == 'GET':
        group = get_object_or_404(BaseGroup, slug=group_slug)
        return HttpResponseRedirect(reverse('%s_members_index' % group.model.lower(), kwargs={'group_slug': group_slug}))
        
    user = request.user    
        
    group = get_object_or_404(group_model, slug=group_slug)
    if request.method == 'GET':
        
        if group.user_is_admin(user):
            members = group.members.all()
        else:
            members = group.get_members()   # excludes invited / requested members
        
        search_terms = request.GET.get('search', '')
        if search_terms:
            members = members.filter(user__profile__name__icontains=search_terms) | \
                            members.filter(user__username__icontains=search_terms) | \
                            members.filter(is_admin=True, admin_title__icontains=search_terms) | \
                            members.filter(user__email__icontains=search_terms)
                            
        return render_to_response(
            template_name,
            {
                'group': group,
                'members': members,
                'is_admin': group.user_is_admin(user),
                'search_terms': search_terms
            },
            context_instance=RequestContext(request),
        )
    elif request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            
            existing_members = GroupMember.objects.filter(group=group, user=member.user)
            
            # General users can only add themselves as members
            # Users cannot have multiple memberships in the same group
            if existing_members.count() == 0 and (user == member.user or user.is_staff or group.user_is_admin(user)):
                if user == member.user:
                    if group.private and not user.is_staff:     # we ignore group admins since they must already be members
                        member.request_status = 'R'             # requested by user
                    else:
                        member.request_status = 'A'             # if public group, assume automatic acceptance
                                                                # ditto for any group if site admin
                else:   
                    add_type = request.POST["add_type"]
                    if add_type == "auto":
                        member.request_status = 'A'             # group / site admin automatically adds user
                    else:
                        member.request_status = 'I'             # another user invited by a group / site admin         
                   
                if not (user.is_staff or group.user_is_admin(user)):
                    # General users cannot make themselves admins
                    member.is_admin = False
                    member.admin_title = ""
                
                member.group = group
                member.save()
                if request.is_ajax():
                    response = render_to_response(
                        "base_groups/ajax-join.html",
                        {
                            'group': group,
                        },
                        context_instance=RequestContext(request),
                    )
                else:
                    response =  HttpResponseRedirect(reverse('%s_member_detail' % group_model._meta.module_name, kwargs={'group_slug': group_slug, 'username': member.user.username}))
                return response
            else:
                if request.is_ajax():
                    response = render_to_response(
                        "base_groups/ajax-join.html",
                        {
                            'group': None,
                        },
                        context_instance=RequestContext(request),
                    )
                else:
                    response = render_to_response(
                        new_template_name,
                        {
                            'group': group,
                            'form': form,
                            'is_admin': group.user_is_admin(user),
                        },
                        context_instance=RequestContext(request),
                    )
            return response
        else:
            return render_to_response(
                new_template_name,
                {
                    'group': group,
                    'form': form,
                    'is_admin': group.user_is_admin(user),
                },
                context_instance=RequestContext(request),
            )

@visibility_required()
def new_member(request, group_slug, group_model=None, form_class=None, template_name=None, index_template_name=None):
    # handle generic call
    if group_model is None and request.method == 'GET':
        group = get_object_or_404(BaseGroup, slug=group_slug)
        return HttpResponseRedirect(reverse('%s_new_member' % group.model.lower(), kwargs={'group_slug': group_slug}))    
        
    group = get_object_or_404(group_model, slug=group_slug)
    user = request.user
    
    if group.user_is_member_or_pending(user) and not group.user_is_admin(user):
        request.user.message_set.create(
            message=_("You are already a member, or pending member, of this %(model)s - see below.") % {"model": group_model._meta.verbose_name,})
        return HttpResponseRedirect(reverse('%s_member_detail' % group.model.lower(), kwargs={'group_slug': group_slug, 'username': user.username}))
    
    if request.method == 'POST':
        return members_index(request, group_slug, group_model, form_class, index_template_name, template_name)
    form = form_class()
    return render_to_response(
        template_name,
        {
            'group': group,
            'form': form,
            'is_admin': group.user_is_admin(user),
        },
        context_instance=RequestContext(request),
    )

@visibility_required()
def member_detail(request, group_slug, username, group_model=None, form_class=None, template_name=None, edit_template_name=None):
    # handle generic call
    if group_model is None and request.method == 'GET':
        group = get_object_or_404(BaseGroup, slug=group_slug)
        return HttpResponseRedirect(reverse('%s_member_detail' % group.model.lower(), kwargs={'group_slug': group_slug, 'username': username}))    
        
    group = get_object_or_404(group_model, slug=group_slug)
    other_user = get_object_or_404(User, username=username)
    member = get_object_or_404(GroupMember, group=group, user=other_user)
    user = request.user
    
    # retrieve details
    if request.method == 'GET':
        return render_to_response(
            template_name,
            {
                'group': group,
                'member': member,
                'is_admin': group.user_is_admin(user),
            },
            context_instance=RequestContext(request),
        )
    # update existing resource
    elif request.method == 'POST':
        form = form_class(request.POST, instance=member)
        # if form saves, return detail for saved resource
        if form.is_valid():
            member = form.save()
            return render_to_response(
                template_name,
                {
                    'group': group,
                    'member': member,
                    'is_admin': group.user_is_admin(user),
                },
                context_instance=RequestContext(request),
            )
        # if save fails, go back to edit_resource page
        else:
            return render_to_response(
                edit_template_name,
                {
                    'group': group,
                    'form': form,
                    'member': member,
                    'is_admin': group.user_is_admin(user),
                },
                context_instance=RequestContext(request),
            )

@group_admin_required()
def edit_member(request, group_slug, username, group_model=None, form_class=None, template_name=None, detail_template_name=None):
    # handle generic call
    if group_model is None and request.method == 'GET':
        group = get_object_or_404(BaseGroup, slug=group_slug)
        return HttpResponseRedirect(reverse('%s_edit_member' % group.model.lower(), kwargs={'group_slug': group_slug, 'username': username}))         
    
    group = get_object_or_404(group_model, slug=group_slug)
    other_user = get_object_or_404(User, username=username)
    user = request.user
    
    if request.method == 'POST':
        # this results in a non-ideal URL (/../edit) but only way we can save changes
        return member_detail(request, group_slug, username, group_model, form_class, detail_template_name, template_name)
    member = get_object_or_404(GroupMember, group=group, user=other_user)
    form = form_class(instance=member)
    return render_to_response(
        template_name,
        {
            'group': group,
            'form': form,
            'member': member,
            'is_admin': group.user_is_admin(user),
        },
        context_instance=RequestContext(request),
    )

@own_member_object_required()
def delete_member(request, group_slug, username, group_model=None):    
    # handle generic call
    if group_model is None and request.method == 'GET':
        group = get_object_or_404(BaseGroup, slug=group_slug)
        return HttpResponseRedirect(reverse('%s_delete_member' % group.model.lower(), kwargs={'group_slug': group_slug, 'username': username}))
        
    if request.method == 'POST':
        group = get_object_or_404(group_model, slug=group_slug)
        user = get_object_or_404(User, username=username)
        member = get_object_or_404(GroupMember, group=group, user=user)
        member.delete()
        if request.is_ajax():
            response = render_to_response(
                "base_groups/ajax-leave.html",
                {
                    'group': group,
                },
                context_instance=RequestContext(request),
            )
        else:
            response =  HttpResponseRedirect(reverse('%s_members_index' % group.model.lower(), kwargs={'group_slug': group_slug,}))
    else:
        if request.is_ajax():
            response = render_to_response(
                "base_groups/ajax-leave.html",
                {
                    'group': None,
                },
                context_instance=RequestContext(request),
            )
        else:
            response = HttpResponseNotFound();
    return response
    
def accept_invitation(request, group_slug, username, group_model=BaseGroup):
    if request.method == 'POST':
        group = get_object_or_404(group_model, slug=group_slug)
        user = get_object_or_404(User, username=username)
        member = get_object_or_404(GroupMember, group=group, user=user, request_status='I')
        
        if request.user.is_authenticated() and user == request.user:
            member.request_status = 'A'
            member.save()
        
        return HttpResponseRedirect(reverse('%s_member_detail' % group.model.lower(), kwargs={'group_slug': group_slug, 'username': username}))
    else:
        return HttpResponseNotFound()
        
def accept_request(request, group_slug, username, group_model=BaseGroup):
    if request.method == 'POST':
        group = get_object_or_404(group_model, slug=group_slug)
        user = get_object_or_404(User, username=username)
        member = get_object_or_404(GroupMember, group=group, user=user, request_status='I')
        
        if request.user.is_authenticated() and group.user_is_admin(request.user):
            member.request_status = 'A'
            member.save()
        
        return HttpResponseRedirect(reverse('%s_member_detail' % group.model.lower(), kwargs={'group_slug': group_slug, 'username': username}))
    else:
        return HttpResponseNotFound()