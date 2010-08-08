"""myEWB user search URLs

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('user_search.views',
    url(r'^search/$', 'user_search', name='profile_user_search'),
    url(r'^samplesearch/$', 'sample_user_search', name='profile_sample_user_search'),
    url(r'^samplemultisearch/$', 'sample_multi_user_search', name='profile_sample_multi_user_search'),
    url(r'^selected/$', 'selected_user', name='selected_user'),
    url(r'^autocomplete/(?P<app>\w+)/(?P<model>\w+)/$', 'autocomplete', name='form_widget_autocomplete')
)
