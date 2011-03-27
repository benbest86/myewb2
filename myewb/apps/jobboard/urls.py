from django.conf.urls.defaults import *

urlpatterns = patterns('jobboard.views',
    url(r'^$', view='list', name="jobboard_list"),
    url(r'^(?P<id>\d+)/$', view='detail', name="jobboard_detail"),

    url(r'^new/$', view='edit', name="jobboard_new"),
    url(r'^(?P<id>\d+)/edit/$', view='edit', name="jobboard_edit"),
)