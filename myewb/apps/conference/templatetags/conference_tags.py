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

@register.simple_tag
def rowspan(length):
    return length / 30

class AttendanceNode(template.Node):
    def __init__(self, session, user, context_attending, context_tentative):
        self.session = template.Variable(session)
        self.user = template.Variable(user)
        self.context_attending = context_attending
        self.context_tentative = context_tentative

    def render(self, context):
        try:
            session = self.session.resolve(context)
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return u''
        
        context[self.context_attending] = session.user_is_attending(user)
        context[self.context_tentative] = session.user_is_tentative(user)
        return u''

def do_attendance(parser, token):
    """
    Provides the template tag {% attendance SESSION USER as ATTENDING TENTATIVE %}
    """
    try:
        _tagname, session, user, _as, context_attending, context_tentative = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(u'%(tagname)r tag syntax is as follows: '
            '{%% %(tagname)r SESSION USER as VARIABLE1 VARIABLE2 %%}' % {'tagname': _tagname})
    return AttendanceNode(session, user, context_attending, context_tentative)

register.tag('attendance', do_attendance)
