"""myEWB base groups template tags

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Last modified on 2009-07-29
@author Joshua Gorner
"""

from django import template
from base_groups.models import GroupMember

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
            
        admins = GroupMember.objects.filter(group=group, is_admin=True)
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

@register.inclusion_tag("base_groups/group_content.html", takes_context=True)
def show_group_content(context, group):
    return {'group': group, 'user': context['user']}
    