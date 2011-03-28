from django import template
from django.contrib.auth.models import User
from group_topics.models import GroupTopic, Watchlist
import settings

register = template.Library()

# thankyou http://djangosnippets.org/snippets/177/
@register.filter
def in_list(value,arg):
    return value in arg
