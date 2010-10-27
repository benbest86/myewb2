from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import NoAuthentication
from confcomm.api import ConferenceProfileHandler, DjangoAuthentication

auth = DjangoAuthentication()
# auth = NoAuthentication()
confprof_handler = Resource(ConferenceProfileHandler, authentication=auth)

# place app url patterns here

urlpatterns = patterns('confcomm.views',
        url('^$', 'index', name='confcomm_index'),
        url('^app/$', 'single_page', name='confcomm_app'),
        url('^register/$', 'register', name='confcomm_register'),

        url('^profile/$', 'profile', name='confcomm_profile'),
        url('^profile/edit/$', 'profile_edit', name='confcomm_profile_edit'),
        url('^profile/(?P<username>\w+)/$', 'profile', name='confcomm_profile'),

        # ajaxified
        url('^piston/profile/(?P<username>\w+)/$', confprof_handler, {'emitter_format': 'json'}, name="confcomm_profile_api"),
        url('^piston/profile/$', confprof_handler, {'emitter_format': 'json'}, name="confcomm_profile_api_base"),
        url('^piston/profiles/$', confprof_handler, {'emitter_format': 'json'}, name="confcomm_profile_api_profiles"),
)
