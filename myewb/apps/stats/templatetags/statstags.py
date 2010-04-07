"""myEWB statistics template tags

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

from django import template
from stats import views

register = template.Library()

@register.simple_tag
def group_membership_breakdown(request, group_slug):
    return views.group_membership_breakdown(request, group_slug)

@register.simple_tag
def group_membership_activity(request, group_slug):
    return views.group_membership_activity(request, group_slug)

@register.simple_tag
def group_post_activity(request, group_slug):
    return views.group_post_activity(request, group_slug)
