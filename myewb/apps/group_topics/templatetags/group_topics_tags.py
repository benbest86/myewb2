"""myEWB group_topic template tags

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2009-12-10
@author: Francis Kung
"""
from django import template
from django.contrib.auth.models import User
from group_topics.models import GroupTopic, Watchlist
import settings

register = template.Library()

@register.simple_tag
def num_topics_for_user(user):
    return GroupTopic.objects.get_for_user(user).count()

class WatchlistNode(template.Node):
    def __init__(self, user, topic, context_name):
        self.user = template.Variable(user)
        self.topic = template.Variable(topic)
        self.context_name = context_name

    def render(self, context):
        try:
            user = self.user.resolve(context)
            topic = self.topic.resolve(context)
        except template.VariableDoesNotExist:
            return u''
        
        try:
            list = Watchlist.objects.get(owner=user)
            context[self.context_name] = list.post_on_list(topic)
        except:
            context[self.context_name] = False
        
        return u''

def topic_on_watchlist(parser, token):
    """
    Provides the template tag {% topic_on_watchlist USER TOPIC as VARIABLE %}
    Returns True if the topic is already on the user's watchlist
    (will need to update when users can have multiple lists)
    """
    try:
        _tagname, user_name, topic_name, _as, context_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(u'%(tagname)r tag syntax is as follows: '
            '{%% %(tagname)r USER TOPIC as VARIABLE %%}' % {'tagname': _tagname})
    return WatchlistNode(user_name, topic_name, context_name)

register.tag('topic_on_watchlist', topic_on_watchlist)

def show_topic_with_user(context, topic):
    return {
        "topic": topic,
        "group": context.get("group"),
        "user": context.get("user"),
        "STATIC_URL": settings.STATIC_URL,
    }
register.inclusion_tag("topics/topic_item.html", takes_context=True)(show_topic_with_user)

@register.simple_tag
def featured_posts_threshold():
    """
    Returns the score needed to get onto the main "featured posts" list.
    (can we do some caching to make this call less expensive?)
    """
    try:
        return GroupTopic.objects.featured()[10].score
    except IndexError:
        return 0
    