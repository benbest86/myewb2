"""myEWB base groups views

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
from django.contrib.contenttypes.models import ContentType
from django.utils.datastructures import SortedDict

from base_groups.models import BaseGroup
from base_groups.helpers import group_search_filter, get_counts, enforce_visibility 
from base_groups.forms import GroupLocationForm
from base_groups.decorators import group_admin_required, visibility_required

from django.conf import settings
if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

def groups_index(request, model=None, member_model=None, form_class=None, template_name='base_groups/groups_index.html',
        new_template_name=None, options=None):
    user = request.user
    if model is None:
        if request.method == 'GET':
            groups = BaseGroup.objects.all()
        
            search_terms = request.GET.get('search', '')
            groups = group_search_filter(groups, search_terms)
            if not user.is_superuser:
                groups = enforce_visibility(groups, user)
            groups = get_counts(groups, BaseGroup)
        
            return render_to_response(
                template_name,
                {
                    'groups': groups,
                    'search_terms': search_terms,
                },
                context_instance=RequestContext(request)
            )
    else:
        if request.method == 'GET':
            groups = model.objects.all()

            search_terms = request.GET.get('search', '')
            groups = group_search_filter(groups, search_terms)
            if not user.is_superuser:
                groups = enforce_visibility(groups, user)
            groups = get_counts(groups, model)

            return render_to_response(
                template_name,
                {
                    'groups': groups,
                    'search_terms': search_terms,
                },
                context_instance=RequestContext(request)
            )
        elif request.method == 'POST':
            form = form_class(request.POST, user=request.user)
            
            allow_create = True
            if options and ("check_create" in options):
                allow_create = request.user.has_perm('%s.add' % model._meta.verbose_name_plural)
            
            if form.is_valid() and allow_create:
                group = form.save(commit=False)
                group.creator = request.user
                group.save()

                group_member = member_model(group=group, user=request.user, is_admin=True, admin_title="Creator")
                group.members.add(group_member)
                group_member.save()

                if notification:
                    # @@@ might be worth having a shortcut for sending to all users
                    notification.send(User.objects.all(), "groups_new_group",
                        {"type": model._meta.verbose_name, "group": group}, queue=True)

                return HttpResponseRedirect(reverse('%s_detail' % model._meta.verbose_name, kwargs={'group_slug': group.slug}))
            else:
                return render_to_response(
                    new_template_name,
                    {
                        'form': form,
                    },
                    context_instance=RequestContext(request)
                )

def new_group(request, model=None, member_model=None, form_class=None, template_name=None, 
        index_template_name=None, options=None):
    if model is None:
        return HttpResponseRedirect(reverse('groups_index'))
    else:
        if request.method == 'POST':
            return groups_index(request, model, member_model, form_class, index_template_name, template_name, options)
        form = form_class(user=request.user)
        return render_to_response(
            template_name,
            {
                'form': form,
            },
            context_instance=RequestContext(request)
        )

@visibility_required()
def group_detail(request, group_slug, model=None, member_model=None, form_class=None, 
        template_name=None, edit_template_name=None, options=None):
    if model is None:
        group = get_object_or_404(BaseGroup, slug=group_slug)
        return HttpResponseRedirect(reverse("%s_detail" % group.model.lower(), kwargs={'group_slug': group_slug}))
    else:
        group = get_object_or_404(model, slug=group_slug)
        if request.user.is_authenticated() and group.user_is_member_or_pending(request.user):
            member = member_model.objects.get(user=request.user, group=group)
        else:
            member = None
        children = group.get_visible_children(request.user)

        # retrieve details
        if request.method == 'GET':
            return render_to_response(
                template_name,
                {
                    'group': group,                
                    'member': member,
                    'children': children,
                },
                context_instance=RequestContext(request)
            )
        # update existing resource
        elif request.method == 'POST':
            form = form_class(request.POST, instance=group, user=request.user)
            # if form saves, return detail for saved resource
            if form.is_valid():
                group = form.save()
                return render_to_response(
                    template_name,
                    {
                        'group': group,                
                        'member': member,
                        'children': children,
                    },
                    context_instance=RequestContext(request)
                )
                # if save fails, go back to edit_resource page
            else:
                return render_to_response(
                    edit_template_name,
                    {
                        'form': form,
                        'group': group,
                    },
                    context_instance=RequestContext(request)
                )

@group_admin_required()
def edit_group(request, group_slug, model=None, member_model=None, form_class=None, 
        template_name=None, detail_template_name=None, options=None):
    if model is None:
        group = get_object_or_404(BaseGroup, slug=group_slug)
        return HttpResponseRedirect(reverse("edit_%s" % group.model.lower(), kwargs={'group_slug': group_slug}))
    else:
        if request.method == 'POST':
            # this results in a non-ideal URL (/<model>s/<slug>/edit) but only way we can save changes
            return group_detail(request, group_slug, model, member_model, form_class, detail_template_name, template_name, options)
        group = get_object_or_404(model, slug=group_slug)
        form = form_class(instance=group, user=request.user)
        return render_to_response(
            template_name,
            {
                'form': form,
                'group': group,
            },
            context_instance=RequestContext(request)
        )

@group_admin_required()
def delete_group(request, group_slug, model=None, member_model=None, form_class=None, 
        detail_template_name=None, options=None):
    if model is None:
        group = get_object_or_404(BaseGroup, slug=group_slug)
        return HttpResponseRedirect(reverse("delete_%s" % group.model.lower(), kwargs={'group_slug': group_slug}))
    else:
        group = get_object_or_404(model, slug=group_slug)
        if request.user.is_authenticated() and group.user_is_member_or_pending(request.user):
            member = member_model.objects.get(user=request.user, group=group)
        else:
            member = None
        children = group.get_visible_children(request.user)

        group_member = member_model.objects.get(group=group, user=request.user)
        if request.method == 'POST':
            if group_member and group_member.is_admin:
                group.delete()
                return HttpResponseRedirect(reverse('%s_index' % model._meta.verbose_name_plural))
            else:
                request.user.message_set.create(
                    message=_("You cannot delete the %(model)s %(group_name)s because you are not an admin.") % {"model": model._meta.verbose_name, "group_name": group.name})
                return render_to_response(
                    detail_template_name,
                    {
                        'group': group,
                        'member': member,
                        'children': children,
                    },
                    context_instance=RequestContext(request)
                )
        else:
            return HttpResponseRedirect(reverse("%s_detail" % group.model.lower(), kwargs={'group_slug': group_slug}))

@group_admin_required()
def group_admin_page(request, group_slug, model=None, member_model=None, template_name=None, options=None):
    if model is None:
        group = get_object_or_404(BaseGroup, slug=group_slug)
        return HttpResponseRedirect(reverse("%s_admin_page" % group.model.lower(), kwargs={'group_slug': group_slug}))
    group = get_object_or_404(model, slug=group_slug)
    if request.user.is_authenticated() and group.user_is_member_or_pending(request.user):
        member = member_model.objects.get(user=request.user, group=group)
    else:
        member = None
    return render_to_response(
            template_name,
            {
                'group': group,
                'member': member,
            },
            context_instance=RequestContext(request))

@group_admin_required()                
def edit_group_location(request, group_slug, model=None, form_class=GroupLocationForm, template_name=None, options=None):
    if model:
        group = get_object_or_404(model, slug=group_slug)
        location = get_object_or_404(GroupLocation, group=group)

        # retrieve details
        if request.method == 'GET':
            form = form_class(instance=location)
            return render_to_response(
                template_name,
                {
                    'form': form,
                    'group': group,
                    'location': location,
                },
                context_instance=RequestContext(request)
            )
        # update existing resource
        elif request.method == 'POST':
            form = form_class(request.POST, instance=location)
            # if form saves, return detail for saved resource
            if form.is_valid():
                location = form.save(commit=False)
                location.group = group
                location.save()
                return render_to_response(
                    template_name,
                    {
                        'form': form,
                        'group': group,
                        'location': location,
                    },
                    context_instance=RequestContext(request)
                )
            # if save fails, go back to edit_resource page
            else:
                return render_to_response(
                    template_name,
                    {
                        'form': form,
                        'group': group,
                        'location': location,
                    },
                    context_instance=RequestContext(request)
                )
