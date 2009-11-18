from django.template import Library
from django.conf import settings

register = Library()

@register.inclusion_tag("whiteboard/whiteboard.html")
def show_whiteboard(whiteboard, group, member):
    return {
        "wb": whiteboard,
        "group": group,
        "member": member,
    }
