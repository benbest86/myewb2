"""myEWB Finance Tool urls

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Alex Joyce
"""

from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^fintest/', include('fintest.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
     (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    
    #needed for debugging on local machine and serving files
#    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'media/', 'show_indexes': False}),

    #if it tries looking down here, it has missed the file so show not found page

)
urlpatterns += patterns('finance.views',
    url(r'^$',                                                                      'index',                name="index"),
    
#    national urls
    url(r'^summary/$',                                                              'summary_no',           name="summary_no"),
    url(r'^summary/(?P<year>\d{4})/(?P<month>\d{1,2})/$',                           'summary_no',           name="summary_no"),
    url(r'^summary/(?P<year>\d{4})/$',                                              'summary_no',           name="summary_no"),
    url(r'^accounts/$',                                                             'account_balances',     name="account_balances"),
    url(r'^budgets/$',                                                              'no_budgets',           name="no_budgets"),
    url(r'^csv/$',                                                                  'csv_trans',            name="csv_trans"),
    url(r'^csv/(?P<year>\d{4})/$',                                                  'csv_trans',            name="csv_trans"),
    url(r'^csv/(?P<year>\d{4})/(?P<month>\d{1,2})/$',                               'csv_trans',            name="csv_trans"),
    url(r'^csv/donationreport/$',                                                   'csv_donationreport',   name="csv_donationreport"),
    url(r'^csv/accountingreport/$',                                                 'csv_accountingreport',   name="csv_accountingreport"),
    url(r'^commitments/upload/$',                                                   'upload_commitments',      name="upload_commitments"),
        url(r'^commitments/view/$',                                                   'noview_commitments',      name="noview_commitments"),
    #    url(r'^monthly_reports/test/$',                                               'create_noreport',      name="create_noreport"),
    url(r'^monthly_reports/dashboard/(?P<year>\d{4})/(?P<month>\d{1,2})/$',         'monthlyreports_dashboard',       name="monthlyreports_dashboard"),
    url(r'^monthly_reports/dashboard/chapter/',                                     'monthlyreports_dashboard',       name="monthlyreports_dashboard"),
    url(r'^monthly_reports/dashboard/national/',                                     'view_allnoreports',       name="view_allnoreports"),
    url(r'^monthly_reports/upload/$',                                               'upload_noreport',      name="upload_noreport"),
      
    
#    chapter specific urls
    url(r'^(?P<group_slug>[-\w]+)/summary/$',                                       'summary',              name="summary"),
    url(r'^(?P<group_slug>[-\w]+)/summary/(?P<year>\d{4})/(?P<month>\d{1,2})/$',    'summary',              name="summary"),
    url(r'^(?P<group_slug>[-\w]+)/summary/(?P<year>\d{4})/$',                       'summary',              name="summary"),
    url(r'^(?P<group_slug>[-\w]+)/$',                                               'index',                name='index'),
    url(r'^(?P<group_slug>[-\w]+)/create/income/$',                                 'create_income',        name="create_income"),
    url(r'^(?P<group_slug>[-\w]+)/create/expenditure/$',                            'create_expenditure',   name="create_expenditure"),
    url(r'^(?P<group_slug>[-\w]+)/create/donation/$',                               'create_donation',      name="create_donation"),
    url(r'^(?P<group_slug>[-\w]+)/filter/$',                                        'filter',               name="filter"),
    url(r'^(?P<group_slug>[-\w]+)/filter/(?P<field>\w+)/$',                         'filterfield',          name="filterfield"),
    url(r'^(?P<group_slug>[-\w]+)/filter/(?P<field>\w+)/(?P<value>\w+)/$',          'filterfieldval',       name="filterfieldval"),

    
    url(r'^(?P<group_slug>[-\w]+)/view/$',                                          'view',                 name="view"),
    url(r'^(?P<group_slug>[-\w]+)/view/(?P<year>\d{4})/$',                          'view',                 name="view"),
    url(r'^(?P<group_slug>[-\w]+)/view/(?P<year>\d{4})/(?P<month>\d{1,2})/$',       'view',                 name="view"),
    url(r'^(?P<group_slug>[-\w]+)/view/commitments/$',                              'view_commitments',     name="view_commitments"),
    url(r'^(?P<group_slug>[-\w]+)/view/detail/(?P<id>\d+)/$',                       'view_id',              name="view_id"),
    url(r'^(?P<group_slug>[-\w]+)/donations/$',                                     'view_donations',       name="view_donations"),
    url(r'^(?P<group_slug>[-\w]+)/donations/(?P<year>\d{4})/$',                     'view_donations',       name="view_donations"),
    url(r'^(?P<group_slug>[-\w]+)/donations/(?P<year>\d{4})/(?P<month>\d{1,2})/$',  'view_donations',       name="view_donations"),

    url(r'^(?P<group_slug>[-\w]+)/edit/$',                                          'edit',                 name="edit"),
    url(r'^(?P<group_slug>[-\w]+)/edit/all/$',                                      'edit_all',             name="edit_all"),
    url(r'^(?P<group_slug>[-\w]+)/edit/(?P<id>\d+)/$',                              'edit_id',              name="edit_id"),
    url(r'^(?P<group_slug>[-\w]+)/delete/(?P<id>\d+)/confirm/$',                    'confirm_delete_id',    name="confirm_delete_id"),
    url(r'^(?P<group_slug>[-\w]+)/delete/(?P<id>\d+)/$',                            'delete_id',            name="delete_id"),
      
    url(r'^(?P<group_slug>[-\w]+)/monthly_reports/$',                               'monthlyreports',       name="monthlyreports"),

    url(r'^(?P<group_slug>[-\w]+)/monthly_reports/submit/confirm/$',                'monthlyreports_submit_confirm',name="monthlyreports_submit_confirm"),
    url(r'^(?P<group_slug>[-\w]+)/monthly_reports/submit/confirm/(?P<year>\d{4})/(?P<month>\d{1,2})/$',                'monthlyreports_submit_confirm',name="monthlyreports_submit_confirm"),    
    url(r'^(?P<group_slug>[-\w]+)/monthly_reports/submit/$',                        'monthlyreports_submit',name="monthlyreports_submit"),
    url(r'^(?P<group_slug>[-\w]+)/monthly_reports/submit/(?P<year>\d{4})/(?P<month>\d{1,2})/$',                   'monthlyreports_submit',name="monthlyreports_submit"),
    url(r'^(?P<group_slug>[-\w]+)/monthly_reports/current/$',                       'monthlyreports_current',name="monthlyreports_current"),
    url(r'^(?P<group_slug>[-\w]+)/monthly_reports/(?P<id>\d+)/csv/',                'csv_monthlyreport',    name="csv_monthlyreport"),
    url(r'^(?P<group_slug>[-\w]+)/monthly_reports/(?P<id>\d+)/$',                   'monthlyreports_id',    name="monthlyreports_id"),
    
    url(r'^(?P<group_slug>[-\w]+)/csv/all/$',                                       'csv_trans',            name="csv_trans"),
    url(r'^(?P<group_slug>[-\w]+)/csv/(?P<year>\d{4})/$',                           'csv_trans',            name="csv_trans"),
    url(r'^(?P<group_slug>[-\w]+)/csv/(?P<year>\d{4})/(?P<month>\d{1,2})/$',        'csv_trans',            name="csv_trans"),
    url(r'^(?P<group_slug>[-\w]+)/csv/donationreport/$',                            'csv_donationreport',   name="csv_donationreport"),
    
    url(r'^(?P<group_slug>[-\w]+)/upload/$',                                        'upload_file',          name="upload_file"),
    
    url(r'^(?P<group_slug>[-\w]+)/upload_testdata/$',                               'upload_testdata',      name="upload_testdata"),
    
    url(r'^(?P<group_slug>[-\w]+)/budget/$',                                        'budgets',              name="budgets"),
    url(r'^(?P<group_slug>[-\w]+)/budget/(?P<budget>\d+)/input/$',                  'input_budgetitems',    name="input_budgetitems"),
    url(r'^(?P<group_slug>[-\w]+)/budget/(?P<budget>\d+)/',                         'view_budget',          name="view_budget"),
    url(r'^(?P<group_slug>[-\w]+)/create/budget/',                                  'create_budget',          name="create_budget"),
    #if down here, then not found
    url(r'.*',                                                                      'page_not_found',       name="page_not_found"),
)
