"""myEWB conference template tags

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

from django import template
from conference.constants import *

register = template.Library()

@register.simple_tag
def lookup_cost(code, room):
    key = "confreg-2011-" + room + "-" + code
    listing = CONF_OPTIONS.get(key, None)
    
    if listing:
        return "$%d &nbsp;&nbsp;&nbsp;(%s)" % (listing['cost'], listing['name'])
    else:
        return ""
    