"""myEWB group_topic template tags

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2009-12-10
@author: Francis Kung
"""
from django import template
from django.contrib.auth.models import User
from group_topics.models import GroupTopic

register = template.Library()

@register.simple_tag
def num_topics_for_user(user):
    return GroupTopic.objects.get_for_user(user).count()