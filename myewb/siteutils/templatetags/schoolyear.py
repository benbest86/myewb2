from datetime import date
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.translation import ugettext_lazy as _
register = template.Library()

@register.filter()
@stringfilter
def schoolyear(year):
    if year == None or year == 'None':
        if date.today().month < 5:
            year = date.today().year - 1
        else:
            year = date.today().year
        
    yr = int(year)
    return "%d-%d" % (yr, yr+1)
