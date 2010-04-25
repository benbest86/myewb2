"""myEWB CHAMP urls

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('champ.views',
    url(r'^$', 'dashboard', name='champ_dashboard'),    
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$', 'dashboard', name='champ_dashboard'),    
    url(r'^(?P<year>\d{4})/(?P<term>[-\w]+)/$', 'dashboard', name='champ_dashboard'),    
    url(r'^(?P<year>\d{4})/$', 'dashboard', name='champ_dashboard'),    
    url(r'^(?P<group_slug>[-\w]+)/$', 'dashboard', name='champ_dashboard'),
    url(r'^(?P<group_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{2})/$', 'dashboard', name='champ_dashboard'),
    url(r'^(?P<group_slug>[-\w]+)/(?P<year>\d{4})/(?P<term>[-\w]+)/$', 'dashboard', name='champ_dashboard'),
    url(r'^(?P<group_slug>[-\w]+)/(?P<year>\d{4})/$', 'dashboard', name='champ_dashboard'),

    url(r'^(?P<group_slug>[-\w]+)/new/', 'new_activity', name="champ_new_activity"),
    url(r'^(?P<group_slug>[-\w]+)/confirmed/', 'confirmed', name="champ_confirmed_activities"),
    url(r'^(?P<group_slug>[-\w]+)/unconfirmed/', 'unconfirmed', name="champ_unconfirmed_activities"),
    #url(r'^activity/(?P<id>\d)/', 'activity_detail', name="champ_activity"),
    url(r'^(?P<group_slug>[-\w]+)/activity/(?P<activity_id>\d)/edit/', 'activity_edit', name="champ_edit_activity"),
    url(r'^(?P<group_slug>[-\w]+)/activity/(?P<activity_id>\d)/confirm/', 'activity_confirm', name="champ_confirm_activity"),
    url(r'^(?P<group_slug>[-\w]+)/activity/(?P<activity_id>\d)/', 'activity_detail', name="champ_activity"),
)
