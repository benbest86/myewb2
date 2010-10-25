from django.conf.urls.defaults import *

# place app url patterns here

urlpatterns = patterns('confcomm.views',
        url('^$', 'index', name='confcomm_index'),
        url('^register/$', 'register', name='confcomm_register'),
)
