"""myEWB base groups views

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Last modified on 2009-12-09
@author Joshua Gorner, Benjamin Best, Francis Kung
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
    
from wiki.models import Article

def groups_index(request, model=None, member_model=None, form_class=None,
                 template_name='base_groups/groups_index.html',
                 new_template_name=None, options=None):
    """
    Display a listing of available groups
    """
    
    if model is None:
        model = BaseGroup
        
    # keep this here to be RESTful (allow POST to index for creating new objects)
    if request.method == 'POST':
        return new_group(request, model=model, member_model=member_model,
                         form_class=form_class, template_name=new_template_name,
                         index_template_name=template_name, options=options)

    # retrieve basic objects
    user = request.user
    groups = model.objects.all()

    # if running a search, filter by search term
    search_terms = request.GET.get('search', '')
    groups = group_search_filter(groups, search_terms)
    
    # visibility check
    # (should we move this into the manager instead?)
    if not user.has_module_perms("base_groups"):
        groups = enforce_visibility(groups, user)
        
    # add some meta-data
    groups = get_counts(groups, model)

    # return listing
    return render_to_response(
        template_name,
        {
            'groups': groups,
            'search_terms': search_terms,
        },
        context_instance=RequestContext(request)
    )

# no decorator - perms depend on type of group
def new_group(request, model=None, member_model=None, form_class=None,
              template_name=None, index_template_name=None, options=None):
    """
    Create a new group
    """
    
    # model can't be None, since we are creating a concrete group
    if model is None:
        return HttpResponseRedirect(reverse('groups_index'))

    # we are on the save leg...
    if request.method == 'POST':
        form = form_class(request.POST, user=request.user)

        # FIXME: this check is obsolete!!! (?)
        allow_create = True
        if options and ("check_create" in options):
            allow_create = request.user.has_perm('%s.add' % model._meta.verbose_name_plural)
        
        # save the group...
        if form.is_valid() and allow_create:
            group = form.save(commit=False)
            group.creator = request.user
            group.save()

            # user is made an admin of the group in a base_group.models
            # post-save hook, no need to do it here.

            if notification:
                # @@@ might be worth having a shortcut for sending to all users
                notification.send(User.objects.all(), "groups_new_group",
                    {"type": model._meta.verbose_name, "group": group}, queue=True)

            return HttpResponseRedirect(reverse('%s_detail' % model._meta.verbose_name, kwargs={'group_slug': group.slug}))

    # create a new form
    else:
        form = form_class(user=request.user)
        
    return render_to_response(template_name,
                              {'form': form},
                              context_instance=RequestContext(request)
                             )

@visibility_required()
def group_detail(request, group_slug, model=None, member_model=None,
                 form_class=None,  template_name=None, edit_template_name=None,
                 options=None):
    """
    View details of a group
    """
    
    # how would we ever get here...??? (is this check redundant?)
    if model is None:
        # find group type and redirect
        group = get_object_or_404(BaseGroup, slug=group_slug)
        return HttpResponseRedirect(reverse("%s_detail" % group.model.lower(), kwargs={'group_slug': group_slug}))
    
    # keep this here to be RESTful (allow POST to object for editing)
    if request.method == 'POST':
        return edit_group(request, group_slug, model=model,
                          member_model=member_model, form_class=form_class,
                          template_name=edit_template_name,
                          detail_template_name=template_Name, options=options)

    # get group
    group = get_object_or_404(model, slug=group_slug)

    # membership status
    if group.user_is_member(request.user):
        member = group.members.get(user=request.user)
    elif group.user_is_pending_member(request.user):
        member = group.pending_members.get(user=request.user)
    else:
        member = None
        
    # retrieve whiteboard (create if needed)
    if group.whiteboard == None:
        wb = Article(title="Whiteboard", content="")
        group.associate(wb, commit=False)
        wb.save()
        group.whiteboard = wb
        group.save()
    
    # render
    return render_to_response(
        template_name,
        {
            'group': group,                
            'children': group.get_visible_children(request.user),
            'is_admin': group.user_is_admin(request.user)
        },
        context_instance=RequestContext(request)
    )
    
@group_admin_required()
def edit_group(request, group_slug, model=None, member_model=None,
               form_class=None, template_name=None, detail_template_name=None,
               options=None):
    """
    Edit an existing group
    """
    
    # how would we ever get here...??? (is this check redundant?)
    if model is None:
        group = get_object_or_404(BaseGroup, slug=group_slug)
        return HttpResponseRedirect(reverse("edit_%s" % group.model.lower(), kwargs={'group_slug': group_slug}))

    # load up group
    group = get_object_or_404(model, slug=group_slug)
    
    # on the save leg
    if request.method == 'POST':
        form = form_class(request.POST, instance=group, user=request.user)
        
        # if form saves, redirect to detail for saved resource
        if form.is_valid():
            group = form.save()
            return HttpResponseRedirect(reverse('%s_detail' % model._meta.verbose_name, kwargs={'group_slug': group.slug}))

        # if save fails, we will eventually go back to edit_resource page

    # on the form leg
    else:
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
def delete_group(request, group_slug, model=None, member_model=None,
                 form_class=None, detail_template_name=None, options=None):
    """
    Delete a group
    """
    
    # how would we ever get here...??? (is this check redundant?)
    if model is None:
        group = get_object_or_404(BaseGroup, slug=group_slug)
        return HttpResponseRedirect(reverse("delete_%s" % group.model.lower(), kwargs={'group_slug': group_slug}))

    # load up the group
    group = get_object_or_404(model, slug=group_slug)

    # only valid as a "POST" request
    if request.method == 'POST':
        group.delete()
        return HttpResponseRedirect(reverse('%s_index' % model._meta.verbose_name_plural))
    
    # shouldn't happen... but just in case...
    else:
        return HttpResponseRedirect(reverse("%s_detail" % group.model.lower(), kwargs={'group_slug': group_slug}))

@group_admin_required()                
def edit_group_location(request, group_slug, model=None,
                        form_class=GroupLocationForm, template_name=None,
                        options=None):
    if model is None:
        model = BaseGroup
    
    # load up group
    group = get_object_or_404(model, slug=group_slug)
    location = get_object_or_404(GroupLocation, group=group)

    # nothing interesting, just display the form
    if request.method == 'GET':
        form = form_class(instance=location)
        
    # update existing resource
    elif request.method == 'POST':
        form = form_class(request.POST, instance=location)
        
        # if form saves, return detail for saved resource
        if form.is_valid():
            location = form.save(commit=False)
            location.group = group
            location.save()
            return HttpResponseRedirect(reverse('%s_detail' % model._meta.verbose_name, kwargs={'group_slug': group.slug}))
        
    return render_to_response(
        template_name,
        {
            'form': form,
            'group': group,
            'location': location,
        },
        context_instance=RequestContext(request)
    )
