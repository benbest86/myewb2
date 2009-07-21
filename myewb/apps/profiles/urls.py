"""myEWB profile URLs

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2009-06-30
Last modified: 2009-07-21
@author: Joshua Gorner
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^username_autocomplete/$', 'misc.views.username_autocomplete_friends', name='profile_username_autocomplete'),
    url(r'^$', 'profiles.views.profiles', name='profile_list'),    
    url(r'^(?P<username>[\w\._-]+)/$', 'profiles.views.profile', name='profile_detail'),
    url(r'^(?P<username>[\w\._-]+)/student/(?P<record_id>\d+)/$', 'profiles.views.student_record', name='profile_student_record'),
    url(r'^(?P<username>[\w\._-]+)/student/$', 'profiles.views.add_student_record', name='profile_add_student_record'),
    url(r'^(?P<username>[\w\._-]+)/work/(?P<record_id>\d+)/$', 'profiles.views.work_record', name='profile_work_record'),
    url(r'^(?P<username>[\w\._-]+)/work/$', 'profiles.views.add_work_record', name='profile_add_work_record'),
)
