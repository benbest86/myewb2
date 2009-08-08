"""myEWB networks template tags

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Last modified on 2009-07-29
@author Joshua Gorner
"""

from django import template

register = template.Library()

@register.inclusion_tag("networks/network_item.html", takes_context=True)
def show_network(context, network):
    return {'network': network, 'request': context['request']}