from django import template
register = template.Library()

@register.inclusion_tag("segmented_control.html")
def segmented_control(base_url, current_page, page_list):
  return {'base_url': base_url, 'current_page':current_page, 'page_list': page_list}
