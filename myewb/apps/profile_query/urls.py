"""myEWB advanced profile query URLs

This file is part of myEWB
Copyright 2010 Engineers Without Borders (Canada)

@author: Francis Kung
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('profile_query.views',
    url(r'^$', 'profilequery', name='profile_query'),    
    url(r'^addprofile/$', 'addprofile', name='profile_query_addprofile'),    
    url(r'^delprofile/(?P<id>\d+)/$', 'delprofile', name='profile_query_delprofile'),    
    url(r'^addgroup/$', 'addgroup', name='profile_query_addgroup'),    
)