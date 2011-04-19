from django import template

from jobboard.models import JobPosting

register = template.Library()

@register.simple_tag
def jobboard_count():
    return JobPosting.objects.open().count()


class JobboardUpcomingNode(template.Node):
    def __init__(self, username, context_name):
        self.user = template.Variable(username)
        self.context_name = context_name

    def render(self, context):
        try:
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return u''

        # TODO: do a fancier, user-based weighting...?
        jobs = JobPosting.objects.open()
        jobs = jobs.filter(urgency__gte='3')
        jobs = jobs.order_by('deadline')[0:4]
        
        context[self.context_name] = jobs
        return u''

def jobboard_upcoming(parser, token):
    """
    Provides the template tag {% jobboard_upcoming for USER as VARIABLE %}
    """
    try:
        _tagname, _for, username, _as, context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(u'%(tagname)r tag syntax is as follows: '
            '{%% %(tagname)r for USER as VARIABLE %%}' % {'tagname': _tagname})
    return JobboardUpcomingNode(username, context_name)

register.tag('jobboard_upcoming', jobboard_upcoming)
