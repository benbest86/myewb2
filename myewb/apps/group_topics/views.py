"""myEWB GroupTopics views

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Created on: 2009-08-13
Last modified: 2009-08-15
@author: Joshua Gorner, Francis Kung
"""

from django.http import HttpResponse, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _
from django.contrib.syndication import feeds

from base_groups.models import BaseGroup
from group_topics.forms import GroupTopicForm
from group_topics.feeds import TopicFeedAll, TopicFeedGroup

from topics.views import *
from topics.views import topics as pinaxtopics

def topics(request, group_slug=None, form_class=GroupTopicForm, template_name="topics/topics.html", bridge=None):
    return pinaxtopics(request, group_slug, form_class, template_name, bridge)

def feed(request, group_slug):
    try:
        if group_slug == 'all':
            feedgen = TopicFeedAll(group_slug, request).get_feed()
        else:
            group = BaseGroup.objects.get(slug=group_slug)
            if group.visibility == 'E' or (request.user.is_authenticated() and group.user_is_member(request.user)):
                feedgen = TopicFeedGroup(group_slug, request).get_feed(group_slug)
            else:
                return HttpResponseForbidden()

    except feeds.FeedDoesNotExist:
        raise Http404, _("Invalid feed parameters. Slug %r is valid, but other parameters, or lack thereof, are not.") % slug

    response = HttpResponse(mimetype=feedgen.mime_type)
    feedgen.write(response, 'utf-8')
    return response
