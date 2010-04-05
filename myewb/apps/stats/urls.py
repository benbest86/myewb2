"""myEWB stats URLs

This file is part of myEWB
Copyright 2010 Engineers Without Borders (Canada)

@author: Francis Kung
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('stats.views',
    url(r'^dashboard/$', 'main_dashboard', name='stats_dashboard'),    
)