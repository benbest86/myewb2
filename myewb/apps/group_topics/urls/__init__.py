"""myEWB GroupTopic URLs

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Created on: 2009-08-13
@author: Joshua Gorner
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'group_topics.views.topics', name="topic_list"),
    url(r'^attach/$', 'group_topics.views.get_attachment_form', name="topic_get_attachment_form"),
    url(r'^(?P<topic_id>\d+)/edit/$', 'group_topics.views.topic', kwargs={"edit": True}, name="topic_edit"),
    url(r'^(?P<topic_id>\d+)/delete/$', 'group_topics.views.topic_delete', name="topic_delete"),
    url(r'^(?P<topic_id>\d+)/$', 'group_topics.views.topic', name="topic_detail"),
    url(r'^user/(?P<username>[\w\._-]+)/$', 'group_topics.views.topics_by_user', name="topic_list_by_user"),
)
