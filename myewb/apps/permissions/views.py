"""myEWB permissions views

This file is part of myEWB
Copyright 2010 Engineers Without Borders (Canada

@author: Francis Kung
"""

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.contrib.admin.views.decorators import staff_member_required

from permissions.forms import AddPermissionForm
from permissions.models import PermissionGroup

# Have chosen not to use our own perms system for this check because giving 
# someone access over the perms system is giving them access to everything...
# so we may as well re-use the is_staff instead.  The number of is_staff site 
# admins should be very small anyway.
@staff_member_required
def permissions_index(request):
    groups = PermissionGroup.objects.all()
    admin_count = User.objects.filter(is_staff=True).count()
    
    return render_to_response("permissions/list.html", {
        "groups": groups,
        "admin_count": admin_count,
    }, context_instance=RequestContext(request))
 
@staff_member_required   
def permissions_detail(request, groupid):
    group = get_object_or_404(PermissionGroup, pk=groupid)
    
    if request.POST:
        form = AddPermissionForm(request.POST)
        if form.is_valid():
            users = form.cleaned_data['user']
            
            for user in users:
                # TODO: check if user is already in group?
                group.user_set.add(user)
                request.user.message_set.create(message="Added %s" % user.visible_name())
                
            # reset form...
            form = AddPermissionForm()
            
            # FIXME: change so we redirect on success, to avoid double-submit-on-refresh
    else:
        form = AddPermissionForm()

    return render_to_response("permissions/detail.html", {
        "group": group,
        "form": form,
    }, context_instance=RequestContext(request))

@staff_member_required   
def permissions_admin_detail(request):
    admins = User.objects.filter(is_staff=True)
    
    if request.POST:
        form = AddPermissionForm(request.POST)
        if form.is_valid():
            users = form.cleaned_data['user']
            
            for user in users:
                user.is_staff = True
                user.is_superuser = True
                user.save()
                request.user.message_set.create(message="Added %s" % user.visible_name())
                
            # reset form...
            form = AddPermissionForm()
            
            # FIXME: change so we redirect on success, to avoid double-submit-on-refresh
    else:
        form = AddPermissionForm()

    return render_to_response("permissions/admin_detail.html", {
        "admins": admins,                                                        
        "form": form,
    }, context_instance=RequestContext(request))

@staff_member_required   
def permissions_remove(request, groupid, userid):
    group = get_object_or_404(PermissionGroup, pk=groupid)
    user = get_object_or_404(User, pk=userid)
    
    group.user_set.remove(user)
    request.user.message_set.create(message="Removed %s" % user.visible_name())

    return HttpResponseRedirect(reverse("permissions_detail", kwargs={'groupid': group.pk}))
    
@staff_member_required   
def permissions_admin_remove(request, userid):
    user = get_object_or_404(User, pk=userid)

    user.is_staff = False
    user.is_superuser = False
    user.save()
    request.user.message_set.create(message="Removed %s" % user.visible_name())

    return HttpResponseRedirect(reverse("permissions_admin_detail", kwargs={}))
    