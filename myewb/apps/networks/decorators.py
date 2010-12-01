from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from base_groups.models import BaseGroup, GroupMember
from communities.models import Community
from siteutils.shortcuts import get_object_or_none

class chapter_president_required(object):
    """
    Checks to see whether the user is chapter president of this chapter.
    Requires that group_slug is first non-request argument. Used with BaseGroup.
    
    Assumptions:
    - you can only be an exec member of one chapter
    - if you are on the chapter presidents' list, and are an exec of a given 
      chapter, then you are chapter president of that chapter 
    """
    def __call__(self, f):
        def newf(request, *args, **kwargs):            
            user = request.user
                        
            if user.has_module_perms("base_groups"):
                return f(request, *args, **kwargs)
            
            group_slug = kwargs.get('group_slug', None) or (len(args) > 0 and args[0])
            if not user.is_authenticated():
                # deny access - would set this to redirect
                # to a custom template eventually
                return render_to_response('denied.html', context_instance=RequestContext(request))
            
            group = get_object_or_404(BaseGroup, slug=group_slug)
            if group.model == 'Network':
                if group.network.user_is_president(user):
                    return f(request, *args, **kwargs)
                
            return render_to_response('denied.html', context_instance=RequestContext(request))
        return newf

class chapter_exec_required(object):
    """
    Checks to see whether the user is an exec of any chapter 
    """
    def __call__(self, f):
        def newf(request, *args, **kwargs):            
            user = request.user
                        
            if user.has_module_perms("base_groups"):
                return f(request, *args, **kwargs)

            if not user.is_authenticated():
                # deny access - would set this to redirect
                # to a custom template eventually
                return render_to_response('denied.html', context_instance=RequestContext(request))
            
            execlist = get_object_or_none(Community, slug='exec')
            if execlist and execlist.user_is_member(user):
                return f(request, *args, **kwargs)
                
            return render_to_response('denied.html', context_instance=RequestContext(request))
        return newf
   