"""myEWB CHAMP template tags

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada
"""

from datetime import date
from django import template
from champ.views import build_filters, run_query
from champ.models import Activity 

register = template.Library()

@register.simple_tag
def champ_activities(group):
    today = date.today()
    
    activity_filters, metric_filters = build_filters(year=today.year, month=today.month)
    activity_filters.append({'group__slug': group.slug})
    print "looking up ", today.year, " m ", today.month
    
    return run_query(Activity.objects.all(), activity_filters).count()

@register.simple_tag
def champ_unconfirmed(group):
    today = date.today()
    
    activity_filters, metric_filters = build_filters(year=today.year, month=today.month)
    activity_filters.append({'group__slug': group.slug})
    
    return run_query(Activity.objects.filter(confirmed=False), activity_filters).count()

@register.simple_tag
def month():
    today = date.today()
    return today.strftime('%B')
