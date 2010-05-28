"""myEWB base groups template tags

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Last modified on 2009-07-29
@author Joshua Gorner
"""

from django import template
from django.contrib.contenttypes.models import ContentType
from group_topics.models import GroupTopic

register = template.Library()

@register.inclusion_tag("base_groups/group_item.html", takes_context=True)
def show_group(context, group):
    return {'group': group, 'request': context['request']}

@register.simple_tag
def clear_search_url(request):
    getvars = request.GET.copy()
    if 'search' in getvars:
        del getvars['search']
    if len(getvars.keys()) > 0:
        return "%s?%s" % (request.path, getvars.urlencode())
    else:
        return request.path

@register.simple_tag
def persist_getvars(request):
    getvars = request.GET.copy()
    if len(getvars.keys()) > 0:
        return "?%s" % getvars.urlencode()
    return ''
    
class AdminsNode(template.Node):
    def __init__(self, group_name, context_name):
        self.group = template.Variable(group_name)
        self.context_name = context_name

    def render(self, context):
        try:
            group = self.group.resolve(context)
        except template.VariableDoesNotExist:
            return u''
            
        admins = group.members.filter(is_admin=True)
        context[self.context_name] = admins
        return u''

def do_get_admins(parser, token):
    """
    Provides the template tag {% get_admins GROUP as VARIABLE %}
    """
    try:
        _tagname, group_name, _as, context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(u'%(tagname)r tag syntax is as follows: '
            '{%% %(tagname)r GROUP as VARIABLE %%}' % {'tagname': _tagname})
    return AdminsNode(group_name, context_name)

register.tag('get_admins', do_get_admins)

class MembershipNode(template.Node):
    def __init__(self, group, user, context_name):
        self.group = template.Variable(group)
        self.user = template.Variable(user)
        self.context_name = context_name

    def render(self, context):
        try:
            group = self.group.resolve(context)
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return u''
            
        # membership status
        if group.user_is_member(user):
            member = group.members.get(user=user)
        elif group.user_is_pending_member(user):
            member = group.pending_members.get(user=user)
        else:
            member = None
        context[self.context_name] = member
        return u''

def do_get_membership(parser, token):
    """
    Provides the template tag {% get_membership GROUP USER as VARIABLE %}
    """
    try:
        _tagname, group, user, _as, context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(u'%(tagname)r tag syntax is as follows: '
            '{%% %(tagname)r GROUP USER as VARIABLE %%}' % {'tagname': _tagname})
    return MembershipNode(group, user, context_name)

register.tag('get_membership', do_get_membership)

# Copied and modified from pinax/apps/topics/templatetags/topics_tags.py
# (only change is to return list of GroupTopic objects instead of Topic -
#  needed for tagging to work)
class GroupTopicsForGroupNode(template.Node):
    def __init__(self, group_name, context_name):
        self.group = template.Variable(group_name)
        self.context_name = context_name

    def render(self, context):
        try:
            group = self.group.resolve(context)
        except template.VariableDoesNotExist:
            return u''
        content_type = ContentType.objects.get_for_model(group)
        context[self.context_name] = GroupTopic.objects.get_for_group(group)
        return u''

def do_get_grouptopics_for_group(parser, token):
    """
    Provides the template tag {% get_topics_for_group GROUP as VARIABLE %}
    """
    try:
        _tagname, group_name, _as, context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(u'%(tagname)r tag syntax is as follows: '
            '{%% %(tagname)r GROUP as VARIABLE %%}' % {'tagname': tagname})
    return GroupTopicsForGroupNode(group_name, context_name)

register.tag('get_grouptopics_for_group', do_get_grouptopics_for_group)
#end copy

class RandomMemberNode(template.Node):
    def __init__(self, group_name, number, context_name):
        self.group = template.Variable(group_name)
        self.context_name = context_name
        self.number = number

    def render(self, context):
        try:
            group = self.group.resolve(context)
        except template.VariableDoesNotExist:
            return u''
            
        members = group.get_accepted_members().order_by('?')[:self.number]
        context[self.context_name] = members
        return u''

def do_get_random_members(parser, token):
    """
    Provides the template tag {% get_random_members GROUP NUMBER as VARIABLE %}
    """
    try:
        _tagname, group_name, number, _as, context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(u'%(tagname)r tag syntax is as follows: '
            '{%% %(tagname)r GROUP NUMBER as VARIABLE %%}' % {'tagname': _tagname})
    return RandomMemberNode(group_name, number, context_name)

register.tag('get_random_members', do_get_random_members)

class GroupIsVisibleNode(template.Node):
    def __init__(self, group_name, username, context_name):
        self.group = template.Variable(group_name)
        self.user = template.Variable(username)
        self.context_name = context_name

    def render(self, context):
        try:
            group = self.group.resolve(context)
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return u''
        
        context[self.context_name] = group.is_visible(user)
        return u''

def do_group_is_visible(parser, token):
    """
    Provides the template tag {% group_is_visible GROUP for USER as VARIABLE %}
    """
    try:
        _tagname, group_name, _for, username, _as, context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(u'%(tagname)r tag syntax is as follows: '
            '{%% %(tagname)r GROUP for USER as VARIABLE %%}' % {'tagname': _tagname})
    return GroupIsVisibleNode(group_name, username, context_name)

register.tag('group_is_visible', do_group_is_visible)
