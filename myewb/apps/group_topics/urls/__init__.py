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
    url(r'^(?P<topic_id>\d+)/print/$', 'group_topics.views.topic', {'template_name': 'topics/printable.html'}, name="topic_printable"),
    url(r'^(?P<topic_id>\d+)/printreplies/$', 'group_topics.views.topic', {'template_name': 'topics/printablereplies.html'}, name="topic_printable_with_replies"),
    url(r'^(?P<topic_id>\d+)/$', 'group_topics.views.topic', name="topic_detail"),
    url(r'^user/(?P<username>[\w\._-]+)/$', 'group_topics.views.topics_by_user', name="topic_list_by_user"),
    url(r'^admin/$', 'group_topics.views.adminovision_toggle', name="topic_adminovision"),
    url(r'^cloud/$', 'django.views.generic.simple.direct_to_template', {'template': 'topics/cloud.html'}, name="topic_cloud"),
    url(r'^list/(?P<list_id>\d+)/$', 'group_topics.views.watchlist', name="topic_watchlist"),
    url(r'^lists/$', 'group_topics.views.watchlist_index', name="topic_watchlists"),
    #url(r'^list/(?P<list_id>\d+)/add/(?P<topic_id>\d+)/$', 'group_topics.views.add_to_watchlist', name="topic_watchlist_add"),
    url(r'^list/(?P<user_id>\d+)/add/(?P<topic_id>\d+)/$', 'group_topics.views.add_to_watchlist', name="topic_watchlist_add"),
    url(r'^list/(?P<user_id>\d+)/remove/(?P<topic_id>\d+)/$', 'group_topics.views.remove_from_watchlist', name="topic_watchlist_remove"),
)
