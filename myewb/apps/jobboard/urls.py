from django.conf.urls.defaults import *

urlpatterns = patterns('jobboard.views',
    url(r'^$', view='list', name="jobboard_list"),
    url(r'^(?P<id>\d+)/$', view='detail', name="jobboard_detail"),

    url(r'^new/$', view='edit', name="jobboard_new"),
    url(r'^(?P<id>\d+)/edit/$', view='edit', name="jobboard_edit"),
    
    url(r'^(?P<id>\d+)/bid/$', view='bid', name="jobboard_bid"),
    url(r'^(?P<id>\d+)/bid/cancel/$', view='bid_cancel', name="jobboard_bid_cancel"),
    url(r'^(?P<id>\d+)/watch/$', view='watch', name="jobboard_watch"),
    url(r'^(?P<id>\d+)/watch/cancel/$', view='watch_cancel', name="jobboard_watch_cancel"),
    
)