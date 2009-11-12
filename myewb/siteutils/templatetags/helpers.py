from django import template
from django.core.urlresolvers import reverse
register = template.Library()

@register.inclusion_tag("new_button.html")
def new_button(item, label=None):
  if label == None:
    label = item
  return {'label': label, 'item_url':reverse("%s_new" % item)}

