from django.contrib.admin.templatetags.admin_list import _boolean_icon

from django import template
register = template.Library()

@register.filter(name='boolean_icon')
def boolean_icon(item):
  return _boolean_icon(item)
