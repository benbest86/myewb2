from django.conf.urls.defaults import *

# place app url patterns here

urlpatterns = patterns('confcomm.views',
        url('^$', 'index', name='confcomm_index'),
        url('^register/$', 'register', name='confcomm_register'),

        url('^profile/$', 'profile', name='confcomm_profile'),
        url('^profile/edit/$', 'profile_edit', name='confcomm_profile_edit'),
        url('^profile/(?P<username>)/$', 'profile', name='confcomm_profile'),
)
