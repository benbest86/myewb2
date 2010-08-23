from django import template
from django.template import Library
from django.conf import settings

from workspace.models import Workspace
from workspace.views import preview_extensions, preview_aliases
from workspace import previews

import os

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

class CanPreviewNode(template.Node):
    def __init__(self, file, context_name):
        self.file = template.Variable(file)
        self.context_name = context_name

    def render(self, context):
        try:
            file = self.file.resolve(context)
        except template.VariableDoesNotExist:
            return u''
        
        # normalize the extension
        ext = file.get_extension()
        if preview_aliases.get(ext, None):
            ext = preview_aliases[ext]
    
        # load up the preview template
        if ext in preview_extensions:
            context[self.context_name] = True
        else:
            context[self.context_name] = False
            
        return u''

def do_can_preview(parser, token):
    """
    Provides the template tag {% can_preview FILE as VARIABLE %}
    """
    try:
        _tagname, file, _as, context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(u'%(tagname)r tag syntax is as follows: '
            '{%% %(tagname)r FILE as VARIABLE %%}' % {'tagname': 'can_preview'})
    return CanPreviewNode(file, context_name)

register.tag('can_preview', do_can_preview)

class PreviewNode(template.Node):
    def __init__(self, workspace, file):
        self.workspace = template.Variable(workspace)
        self.file = template.Variable(file)

    def render(self, context):
        try:
            workspace = self.workspace.resolve(context)
            file = self.file.resolve(context)
        except template.VariableDoesNotExist:
            return u''
        
        # normalize the extension
        ext = file.get_extension()
        if preview_aliases.get(ext, None):
            ext = preview_aliases[ext]
    
        if ext in preview_extensions:
            try:
                # dynamically load the preview renderer
                m = __import__('workspace.previews.%s' % ext,
                               globals(), locals(), ['render'], -1)
                return m.render(workspace, file)
            except:
                pass
    
        return u''

def do_preview(parser, token):
    """
    Provides the template tag {% preview WORKSPACE FILE as VARIABLE %}
    """
    try:
        _tagname, workspace, file = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(u'%(tagname)r tag syntax is as follows: '
            '{%% %(tagname)r WORKSPACE FILE %%}' % {'tagname': 'preview'})
    return PreviewNode(workspace, file)

register.tag('preview', do_preview)

class PermsNode(template.Node):
    def __init__(self, workspace, user, context_name1, context_name2):
        self.workspace = template.Variable(workspace)
        self.user = template.Variable(user)
        self.context_name1 = context_name1
        self.context_name2 = context_name2

    def render(self, context):
        try:
            workspace = self.workspace.resolve(context)
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return u''

        context[self.context_name1] = workspace.user_can_view(user)
        context[self.context_name2] = workspace.user_can_edit(user)
        return u''

def do_workspace_perms(parser, token):
    """
    Provides the template tag {% workspace_perms WORKSPACE USER as VIEW_VARIABLE EDIT_VARIABLE %}
    """
    try:
        _tagname, workspace, user, _as, context_name1, context_name2 = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(u'%(tagname)r tag syntax is as follows: '
            '{%% %(tagname)r WORKSPACE USER as VIEW_VARIABLE EDIT_VARIABLE %%}' % {'tagname': 'workspace_perms'})
    return PermsNode(workspace, user, context_name1, context_name2)

register.tag('workspace_perms', do_workspace_perms)

