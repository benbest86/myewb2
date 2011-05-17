"""myEWB permissions URLs

This file is part of myEWB
Copyright 2010 Engineers Without Borders (Canada)

@author: Francis Kung
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('permissions.views',
    url(r'^$', 'permissions_index', name='permissions_index'),    
    url(r'^admin/$', 'permissions_admin_detail', name='permissions_admin_detail'),    
    url(r'^(?P<groupid>\d+)/$', 'permissions_detail', name='permissions_detail'),    
    url(r'^remove/(?P<groupid>\d+)/(?P<userid>\d+)/$', 'permissions_remove', name='permissions_remove'),    
    url(r'^remove/admin/(?P<userid>\d+)/$', 'permissions_admin_remove', name='permissions_admin_remove'),    
)