from django.http import HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.contrib.auth.models import User
from base_groups.models import BaseGroup, GroupMember

class group_admin_required(object):
    """
    Checks to see whether the user is an admin. 
    Requires that group_slug is first non-request argument. Used with BaseGroup.
    """
    def __call__(self, f):
        def newf(request, *args, **kwargs):            
            user = request.user            
            group_slug = kwargs.get('group_slug', None) or (len(args) > 0 and args[0])
            if not user.is_authenticated():
                # deny access - would set this to redirect
                # to a custom template eventually
                return render_to_response('denied.html', context_instance=RequestContext(request))
            
            group = get_object_or_404(BaseGroup, slug=group_slug)
            if group.user_is_admin(user):
                # add object to list of kwargs because we had to hit
                # the database to get it - no point in doing that
                # again in the view function
                return f(request, *args, **kwargs)
            else:
                # deny access
                return render_to_response('denied.html', context_instance=RequestContext(request))
        return newf
        
class group_membership_required(object):
    """
    Checks to see whether the user is a member of the group.
    Requires that group_slug is first non-request argument. Used with BaseGroup.
    """
    def __call__(self, f):
        def newf(request, *args, **kwargs):            
            user = request.user            
            group_slug = kwargs.get('group_slug', None) or (len(args) > 0 and args[0])
            group = get_object_or_404(BaseGroup, slug=group_slug)
            if group.user_is_member(user, admin_override=True):
                return f(request, *args, **kwargs)
            else:
                # deny access
                return render_to_response('denied.html', context_instance=RequestContext(request))
        return newf
        
class own_member_object_required(object):
    """
    Checks to see whether the user is the member in question (or a group admin).
    Requires that group_slug is first non-request argument, and username is second.
    Used with GroupMember.
    """

    def __call__(self, f):
        def newf(request, *args, **kwargs):
            user = request.user
            group_slug = kwargs.get('group_slug', None) or (len(args) > 0 and args[0])
            username = kwargs.get('username', None) or (len(args) > 1 and args[1])
            if not user.is_authenticated():
                # deny access - would set this to redirect
                # to a custom template eventually
                return render_to_response('denied.html', context_instance=RequestContext(request))
            
            group = get_object_or_404(BaseGroup, slug=group_slug)
            other_user = get_object_or_404(User, username=username)
            if user == other_user or group.user_is_admin(user):
                # add object to list of kwargs because we had to hit
                # the database to get it - no point in doing that
                # again in the view function
                return f(request, *args, **kwargs)
            else:
                # deny access
                return render_to_response('denied.html', context_instance=RequestContext(request))
        return newf

class visibility_required(object):
    
    def __call__(self, f):
        def newf(request, *args, **kwargs):
            user = request.user
            group_slug = kwargs.get('group_slug', None) or (len(args) > 0 and args[0])

            group = get_object_or_404(BaseGroup, slug=group_slug)
            if group.is_visible(user):
                return f(request, *args, **kwargs)
            else:
                # deny access
                return render_to_response('denied.html', context_instance=RequestContext(request))
        return newf
