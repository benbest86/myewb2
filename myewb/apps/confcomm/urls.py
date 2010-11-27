from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import NoAuthentication
from confcomm.api import ConferenceProfileHandler, DjangoAuthentication, \
        CohortHandler, CohortMemberHandler

auth = DjangoAuthentication()
noauth = NoAuthentication()
confprof_handler = Resource(ConferenceProfileHandler, authentication=auth)
cohort_handler = Resource(CohortHandler, authentication=noauth)
cohort_member_handler = Resource(CohortMemberHandler, authentication=auth)

# place app url patterns here

urlpatterns = patterns('confcomm.views',
        url('^$', 'single_page', name='confcomm_app'),
        url('^app/$', 'single_page', name='confcomm_app_full'),
        url('^register/$', 'register', name='confcomm_register'),
        url('^login/$', 'login', name='confcomm_login'),

        url('^profile/$', 'profile', name='confcomm_profile'),
        url('^profile/edit/$', 'profile_edit', name='confcomm_profile_edit'),
        url('^profile/(?P<username>\.?\w+)/$', 'profile', name='confcomm_profile'),

        # ajaxified
        url('^send_invitation/$', 'send_invitation', name='confcomm_email'),
        url('^update_avatar/$', 'update_avatar', name='confcomm_avatar'),
        url('^piston/profile/(?P<username>\.?[\w\._-]+)/$', confprof_handler, {'emitter_format': 'json'}, name="confcomm_profile_api"),
        url('^piston/profile/$', confprof_handler, {'emitter_format': 'json'}, name="confcomm_profile_api_base"),
        url('^piston/profiles/$', confprof_handler, {'emitter_format': 'json'}, name="confcomm_profile_api_profiles"),
        url('^piston/cohorts/$', cohort_handler, {'emitter_format': 'json'}, name='confcomm_cohorts'),
        url('^piston/cohort_members/$', cohort_member_handler, {'emitter_format': 'json'}, name='confcomm_cohort_members'),
        url('^piston/cohort_members/(?P<id>\d+)/$', cohort_member_handler, {'emitter_format': 'json'}, name='confcomm_cohort_members'),
        url('^piston/cohort_members/(?P<id>\d+)/(?P<username>\.?[\w\._-]+)/$', cohort_member_handler, {'emitter_format': 'json'}, name='confcomm_cohort_members'),
)
