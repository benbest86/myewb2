from django.template import Library
from django.conf import settings

from workspace.models import Workspace

register = Library()

@register.inclusion_tag("workspace/workspace.html", takes_context=True)
def show_workspace(context, object, user):
    """
    Show a workspace.
    """
    
    workspace = Workspace.objects.get_for_object(object)
    # TODO: perm check
    
    return {
        "workspace": workspace,
        "STATIC_URL": settings.STATIC_URL,
        "request": context['request']
    }
