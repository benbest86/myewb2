"""myEWB GroupTopic URLs (groups)

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Created on: 2009-08-13
@author: Joshua Gorner
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'group_topics.views.topics', name="topic_list"),
)
