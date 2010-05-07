"""myEWB profile URLs

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2009-06-30
Last modified: 2009-08-12
@author: Joshua Gorner, Francis Kung
"""
from django.conf.urls.defaults import *
from creditcard.forms import PaymentForm
from profiles.forms import MembershipForm, MembershipFormPreview

urlpatterns = patterns('profiles.views.profile',
    url(r'^$', 'profiles', name='profiles_index'),    
    url(r'^$', 'profiles', name='profile_list'),    
    url(r'^edit/$', 'profile_edit', name='profile_edit'),
    url(r'^mass_delete/$', 'mass_delete', name='mass_delete'),
    url(r'^settings/$', 'settings', name='profile_settings'),
    url(r'^(?P<username>[\w\._-]+)/settings/$', 'settings', name='profile_settings'),
    
    url(r'^(?P<username>[\w\._-]+)/$', 'profile', name='profile_detail'),
    url(r'^(?P<username>[\w\._-]+)/membership/$', 'pay_membership', name='profile_pay_membership'),
    url(r'^(?P<username>[\w\._-]+)/membership2/$', 'pay_membership2', name='profile_pay_membership2'),
    url(r'^(?P<username>[\w\._-]+)/membership/preview/$', MembershipFormPreview(PaymentForm), name='profile_pay_preview'),

    url(r'^(?P<username>[\w\._-]+)/impersonate/$', 'impersonate', name='profile_impersonate'),
    url(r'^(?P<username>[\w\._-]+)/delete/$', 'softdelete', name='account_delete'),

    url(r'^(?P<username>[\w\._-]+)/student/(?P<student_record_id>\d+)/$', 'student_record_detail', name='profile_student_record'),
    url(r'^(?P<username>[\w\._-]+)/student/(?P<student_record_id>\d+)/$', 'student_record_detail', name='student_record_detail'),
    url(r'^(?P<username>[\w\._-]+)/student/(?P<student_record_id>\d+)/delete/$', 'delete_student_record', name='delete_student_record'),
    url(r'^(?P<username>[\w\._-]+)/student/$', 'student_records_index', name='student_records_index'),
    url(r'^(?P<username>[\w\._-]+)/student/new/$', 'new_student_record', name='new_student_record'),
    url(r'^(?P<username>[\w\._-]+)/student/(?P<student_record_id>\d+)/edit/$', 'edit_student_record', name='edit_student_record'),

    url(r'^(?P<username>[\w\._-]+)/work/(?P<work_record_id>\d+)/$', 'work_record_detail', name='profile_work_record'),
    url(r'^(?P<username>[\w\._-]+)/work/(?P<work_record_id>\d+)/$', 'work_record_detail', name='work_record_detail'),
    url(r'^(?P<username>[\w\._-]+)/work/(?P<work_record_id>\d+)/delete/$', 'delete_work_record', name='delete_work_record'),
    url(r'^(?P<username>[\w\._-]+)/work/$', 'work_records_index', name='work_records_index'),
    url(r'^(?P<username>[\w\._-]+)/work/new/$', 'new_work_record', name='new_work_record'),
    url(r'^(?P<username>[\w\._-]+)/work/(?P<work_record_id>\d+)/edit/$', 'edit_work_record', name='edit_work_record'),

    url(r'^toolbar/(?P<action>[-\w]+)/(?P<toolbar_id>[-\w]+)/$', 'toolbar_action', name='profile_toolbar_action'),
    url(r'^toolbar/$', 'toolbar_action', name='profile_toolbar_action'), # never called. but needed to hack up with javascript later.
    )

urlpatterns += patterns('profiles.views.address',
    url(r'^(?P<username>[\w\._-]+)/address/$', 'address_index', name='profile_address_index'),
    url(r'^(?P<username>[\w\._-]+)/address/new/$', 'new_address', name='profile_new_address'),
    url(r'^(?P<username>[\w\._-]+)/address/(?P<label>[\w\._-]+)/$', 'address_detail', name='profile_address_detail'),
    url(r'^(?P<username>[\w\._-]+)/address/(?P<label>[\w\._-]+)/delete/$', 'delete_address', name='profile_delete_address'),
    url(r'^(?P<username>[\w\._-]+)/address/(?P<label>[\w\._-]+)/edit/$', 'edit_address', name='profile_edit_address'),
)

urlpatterns = urlpatterns + patterns('pinax.apps.autocomplete_app.views',
    url(r'^username_autocomplete/$', 'username_autocomplete_friends', name='profile_username_autocomplete'),
)
