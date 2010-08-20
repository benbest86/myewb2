from django import template
from django.template import Library
from django.conf import settings

from workspace.models import Workspace
from workspace.views import preview_extensions, preview_aliases

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
        filename, ext = os.path.splitext(file)
        ext = ext[1:]
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

