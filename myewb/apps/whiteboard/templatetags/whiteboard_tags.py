from django.template import Library
from django.conf import settings

register = Library()

@register.inclusion_tag("whiteboard/whiteboard.html")
def show_whiteboard(whiteboard, group, member):
    """
    Show a whiteboard.  If the whiteboard is empty, show a link to create one.
    """
    return {
        "wb": whiteboard,
        "group": group,
        "member": member,
        "force": False,
        "STATIC_URL": settings.STATIC_URL
    }

@register.inclusion_tag("whiteboard/whiteboard.html")
def show_whiteboard_force(whiteboard, group, member):
    """
    Show a whiteboard, even if it's empty.
    """
    return {
        "wb": whiteboard,
        "group": group,
        "member": member,
        "force": True,
        "STATIC_URL": settings.STATIC_URL
    }

