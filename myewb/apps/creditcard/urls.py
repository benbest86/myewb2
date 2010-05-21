"""myEWB credit card URLs

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2009-08-12
Last modified: 2009-08-12
@author: Francis Kung
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('creditcard.views',
    url(r'^$', 'payment', name='payments_index'),    
    url(r'^preview/$', 'payment_preview', name='payment_preview'),
)