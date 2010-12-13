import urllib
from django.utils import simplejson
from django import template
register = template.Library()

class PerspectivesNode(template.Node):
    def __init__(self, user, context_name):
        self.user = template.Variable(user)
        self.context_name = context_name
        
    def render(self, context):
        try:
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return u''

        params = {}
        if user.is_authenticated():
            params['user'] = user.id
    
        encoded = urllib.urlencode(params)
        handle = urllib.urlopen("http://localhost/permagoo/myewbapi.php",
                                encoded)
        
        json = handle.read()
        try:
            obj = simplejson.loads(json)
        except:
            obj = {}
    
        context[self.context_name] = obj
        return u''

def perspectives(parser, token):
    try:
        _tagname, user_name, _as, context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(u'%(tagname)r tag syntax is as follows: '
            '{%% %(tagname)r USER as VARIABLE %%}' % {'tagname': _tagname})
    return PerspectivesNode(user_name, context_name)

register.tag('perspectives', perspectives)
