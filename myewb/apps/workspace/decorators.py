from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from workspace.models import Workspace

class can_view(object):
    """
    Checks permission to view this workspace.
    Requires that workspace_id be one of the keyword arguments.
    
    This requires that the object owning the workspace implement a function
    called workspace_view_perms(user); if this does not exist, permission
    is implicitly granted.
    """
    def __call__(self, f):
        def newf(request, *args, **kwargs):            
            user = request.user
            workspace_id = kwargs['workspace_id']
            workspace = get_object_or_404(Workspace, id=workspace_id)

            if workspace.user_can_view(user):
                return f(request, *args, **kwargs)
            else:
                return render_to_response('denied-ajax.html', context_instance=RequestContext(request))
            
        return newf
        
class can_edit(object):
    """
    Checks permission to view this workspace.
    Requires that workspace_id be one of the keyword arguments.
    
    This requires that the object owning the workspace implement a function
    called workspace_edit_perms(user).
    If this does not exist, we fall back to workspace_view_perms; if this does 
    not exist either, permission is implicitly granted.
    """
    def __call__(self, f):
        def newf(request, *args, **kwargs):            
            user = request.user
            workspace_id = kwargs['workspace_id']
            workspace = get_object_or_404(Workspace, id=workspace_id)

            if workspace.user_can_edit(user):
                return f(request, *args, **kwargs)
            else:
                return render_to_response('denied-ajax.html', context_instance=RequestContext(request))
        return newf

