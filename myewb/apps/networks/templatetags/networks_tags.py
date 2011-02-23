"""myEWB networks template tags

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Last modified on 2009-07-29
@author Joshua Gorner
"""

from datetime import date
from django import template
from django.core.urlresolvers import reverse
from siteutils import schoolyear

register = template.Library()

@register.inclusion_tag("networks/network_item.html", takes_context=True)
def show_network(context, network):
    return {'network': network, 'request': context['request']}

@register.simple_tag
def link_to_current_champ(user):
    chapter = user.get_profile().get_chapter()
    if chapter and chapter.is_chapter():
        return reverse('champ_dashboard', kwargs={'group_slug': chapter.slug,
                                                  'year': schoolyear.school_year()})
    else:
        return reverse('champ_dashboard', kwargs={'year': schoolyear.school_year()})
    
@register.simple_tag
def link_to_current_champ_by_group(user, group):
        return reverse('champ_dashboard', kwargs={'group_slug': group.slug,
                                                  'year': schoolyear.school_year()})
@register.simple_tag
def link_to_current_champ_national():
        return reverse('champ_dashboard', kwargs={'year': schoolyear.school_year()})
    
@register.simple_tag
def link_to_current_finance(user):
    chapter = user.get_profile().get_chapter()
    if chapter and chapter.is_chapter():
        return reverse('summary', kwargs={'group_slug': chapter.slug})
    elif user.has_module_perms('finance'):
        return reverse('index')
    else:
        return None
