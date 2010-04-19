"""myEWB CHAMP urls

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

from django.conf.urls.defaults import *

urlpatterns = patterns('champ.views',
    url(r'^$', 'national_dashboard', name='champ_national_dashboard'),    
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$', 'national_dashboard', name='champ_national_dashboard'),    
    url(r'^(?P<year>\d{4})/(?P<term>[-\w]+)/$', 'national_dashboard', name='champ_national_dashboard'),    
    url(r'^(?P<year>\d{4})/$', 'national_dashboard', name='champ_national_dashboard'),    
    url(r'^(?P<group_slug>[-\w]+)/$', 'group_dashboard', name='champ_group_dashboard'),
    url(r'^(?P<group_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{2})/$', 'group_dashboard', name='champ_group_dashboard'),
    url(r'^(?P<group_slug>[-\w]+)/(?P<year>\d{4})/(?P<term>[-\w]+)/$', 'group_dashboard', name='champ_group_dashboard'),
    url(r'^(?P<group_slug>[-\w]+)/(?P<year>\d{4})/$', 'group_dashboard', name='champ_group_dashboard')

)
