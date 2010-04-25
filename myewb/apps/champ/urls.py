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
)
