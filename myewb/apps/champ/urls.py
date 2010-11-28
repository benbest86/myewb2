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
    url(r'^(?P<group_slug>[-\w]+)/activity/(?P<activity_id>\d+)/edit/', 'activity_edit', name="champ_edit_activity"),
    url(r'^(?P<group_slug>[-\w]+)/activity/(?P<activity_id>\d+)/confirm/', 'activity_confirm', name="champ_confirm_activity"),
    url(r'^(?P<group_slug>[-\w]+)/activity/(?P<activity_id>\d+)/unconfirm/', 'activity_unconfirm', name="champ_unconfirm_activity"),
    url(r'^(?P<group_slug>[-\w]+)/activity/(?P<activity_id>\d+)/delete/', 'activity_delete', name="champ_activity_delete"),
    url(r'^(?P<group_slug>[-\w]+)/activity/(?P<activity_id>\d+)/', 'activity_detail', name="champ_activity"),

    url(r'^(?P<group_slug>[-\w]+)/journal/browse/', 'journal_list', name="champ_journal_list"),
    url(r'^(?P<group_slug>[-\w]+)/journal/new/', 'journal_new', name="champ_journal_new"),
    url(r'^(?P<group_slug>[-\w]+)/journal/(?P<journal_id>\d+)/', 'journal_detail', name="champ_journal_detail"),
    
    url(r'^(?P<group_slug>[-\w]+)/yearplan/(?P<year>\d{4})/', 'yearplan', name="champ_yearplan"),
    url(r'^(?P<group_slug>[-\w]+)/yearplan/', 'yearplan', name="champ_yearplan"),
    
    url(r'^(?P<group_slug>[-\w]+)/csv/so/', 'csv_so', name="champ_csv_so"),
    url(r'^(?P<group_slug>[-\w]+)/csv/all/', 'csv_all', name="champ_csv"),
    url(r'^csv/so/', 'csv_global_so', name="champ_global_csv_so"),
    url(r'^csv/all/', 'csv_global_all', name="champ_global_csv"),
)
