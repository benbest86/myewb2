"""myEWB advanced profile query URLs

This file is part of myEWB
Copyright 2010 Engineers Without Borders (Canada)

@author: Francis Kung
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('profile_query.views',
    url(r'^$', 'query.profilequery', name='profile_query'),    
    url(r'^addprofile/$', 'query.addprofile', name='profile_query_addprofile'),    
    url(r'^delprofile/(?P<id>\d+)/$', 'query.delprofile', name='profile_query_delprofile'),    
    url(r'^addgroup/$', 'query.addgroup', name='profile_query_addgroup'),    

    url(r'^email/compose/$', 'email.compose', name='profile_query_new_email'),
    url(r'^email/preview/$', 'email.preview', name='profile_query_preview_email'),    
    url(r'^email/send/$', 'email.send', name='profile_query_send_email'),    
)