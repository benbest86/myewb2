from django.conf.urls.defaults import *

urlpatterns = patterns('jobboard.views',
    url(r'^$', view='list', name="jobboard_list"),
    url(r'^view/(?P<id>\d+)/$', view='detail', name="jobboard_detail"),
)