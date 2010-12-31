"""myEWB conference registration URLs

This file is part of myEWB
Copyright 2009 Engineers Without Borders Canada

Created on: 2009-10-18
@author: Francis Kung
"""
from django.conf.urls.defaults import *
from conference.forms import ConferenceRegistrationForm, ConferenceRegistrationFormPreview

urlpatterns = patterns('conference.views',
    url(r'^$', 'view_registration', name='confreg'),    
    url(r'^login/$', 'login', name='conference_login'),    
    url(r'^preview/$', 'registration_preview', name='conference_preview'),
    url(r'^receipt/$', 'receipt', name='conference_receipt'),    
    url(r'^cancel/$', 'cancel', name='conference_cancel'),    
    url(r'^list/$', 'list', name='conference_list'),    
    url(r'^list/(?P<chapter>[\w\._-]+)$', 'list', name='conference_list_chapter'),    
    url(r'^codes/$', 'generate_codes', name='conference_codes'),
    url(r'^codelookup/$', 'lookup_code', name='conference_code_lookup')    ,

    url(r'^download/all/$', 'download', kwargs={'who': 'all'}, name='conference_download_all'),
    url(r'^download/chapter/$', 'download', kwargs={'who': 'chapter'}, name='conference_download_chapter'),
    url(r'^download/open/$', 'download', kwargs={'who': 'open'}, name='conference_download_open'),
    url(r'^download/alumni/$', 'download', kwargs={'who': 'alumni'}, name='conference_download_alumni'),
    url(r'^download/external/$', 'download', kwargs={'who': 'external'}, name='conference_download_external'),
	
    (r'^who/', include('confcomm.urls')),
)

urlpatterns += patterns('conference.schedule',
    url(r'^schedule/$', 'schedule', name='conference_schedule'),
    url(r'^schedule/print/$', 'print_schedule', name='conference_print'),
    url(r'^schedule/day/(?P<day>[\w]+)/(?P<stream>[\w]+)/$', 'day', name='conference_by_day'),
    url(r'^schedule/time/(?P<day>[\w]+)/(?P<time>[\d]+)/$', 'time', name='conference_by_time'),
    url(r'^schedule/room/(?P<room>[\d]+)/$', 'room', name='conference_by_room'),
    url(r'^schedule/stream/(?P<stream>[\w]+)/$', 'stream', name='conference_by_stream'),
    
    url(r'^schedule/session/(?P<session>[\d]+)/$', 'session_detail', name='conference_session'),
    url(r'^schedule/session/(?P<session>[\d]+)/edit/$', 'session_edit', name='conference_session_edit'),
    url(r'^schedule/session/(?P<session>[\d]+)/delete/$', 'session_delete', name='conference_session_delete'),
    url(r'^schedule/session/new/$', 'session_new', name='conference_session_new'),

    url(r'^schedule/(?P<session>[\d]+)/attend/$', 'session_attend', name='conference_session_attend'),
    url(r'^schedule/(?P<session>[\d]+)/tentative/$', 'session_tentative', name='conference_session_tentative'),
    url(r'^schedule/(?P<session>[\d]+)/skip/$', 'session_skip', name='conference_session_skip'),
    url(r'^schedule/block/$', 'block', name='conference_block'),
)

