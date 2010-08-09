from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template

from django.shortcuts import render_to_response
from django.template import RequestContext

from django.views.generic import list_detail, create_update
from volunteering.models import *
from volunteering.forms import *
from siteutils.countries import EWB_PLACEMENTS

urlpatterns = patterns('volunteering.views',
    url(r'^$', direct_to_template, {"template": "volunteering/volunteering.html"}, name="volunteering_index"),
    url(r'^ov_info/$', "ov_info", name="ov_info"),
)

### APPLICATION SESSIONS
urlpatterns += patterns('volunteering.views.sessions',
  url(r'^sessions/$', 'sessions', name="sessions"),
  url(r'^sessions/(?P<object_id>\d+)/$', 'session_detail', name="session_detail"),
  url(r'^sessions/(?P<object_id>\d+)/edit/$', 'session_edit', name="session_edit"),
  url(r'^sessions/(?P<new_id>\d+)/new/$', 'session_clone', name="session_new"),
  url(r'^sessions/new/$', 'session_edit', name="session_new"),
)

urlpatterns += patterns('volunteering.views.sessions',
  url(r'^questions/(?P<object_id>\d+)/$', 'question_edit', name="question_edit"),
  url(r'^questions/new/(?P<session_id>\d+)/$', 'question_new',name="question_new"),
  url(r'^questions/reorder/$', 'question_reorder',name="question_reorder"),
  url(r'^questions/delete/$', 'question_delete',name="question_delete"),
  url(r'^intquestions/(?P<object_id>\d+)/$', 'interview_question_edit', name="interview_question_edit"),
  url(r'^intquestions/new/(?P<session_id>\d+)/$', 'interview_question_new',name="interview_question_new"),
  url(r'^intquestions/reorder/$', 'interview_question_reorder',name="interview_question_reorder"),
  url(r'^intquestions/delete/$', 'interview_question_delete',name="interview_question_delete"),
)

urlpatterns += patterns('volunteering.views.sessions',
  url(r'^criteria/(?P<object_id>\d+)/$', 'criteria_edit', name="criteria_edit"),
  url(r'^criteria/new/(?P<session_id>\d+)/$', 'criteria_new',name="criteria_new"),
  url(r'^criteria/reorder/$', 'criteria_reorder',name="criteria_reorder"),
  url(r'^criteria/delete/$', 'criteria_delete',name="criteria_delete"),
)

casestudy_info = {
  'queryset': CaseStudy.objects.all(),
  'template_name': 'volunteering/casestudy/list.html',
  'template_object_name': 'casestudy',
  'paginate_by': 10,
}

casestudy_info_edit = {
  'template_name': 'volunteering/casestudy/form.html',
  'template_object_name': 'casestudy',
  'form_class':  CaseStudyForm,
}

casestudy_info_new = {
  'template_name': 'volunteering/casestudy/form.html',
  'form_class':  CaseStudyForm,
  'post_save_redirect': '/volunteering/casestudys/',
}

urlpatterns += patterns('',
  url(r'^casestudies/$', list_detail.object_list, casestudy_info, name="casestudies"),
  url(r'^casestudies/(?P<object_id>\d+)/$', create_update.update_object, casestudy_info_edit, name="casestudy_detail"),
  url(r'^casestudies/new$', create_update.create_object, casestudy_info_new, name="casestudy_new"),
)


### APPLICATIONS
urlpatterns += patterns('volunteering.views.applications',
  url(r'^applications/$', 'applications', name="applications"),
  url(r'^applications/new/(?P<session_id>\d+)/$', 'application_new', name="applications_new"),
  url(r'^applications/(?P<app_id>\d+)/$', 'application_edit', name="applications_edit"),
  url(r'^applications/(?P<app_id>\d+)/reopen/$', 'application_reopen', name="applications_reopen"),
  url(r'^applications/(?P<app_id>\d+)/view/$', 'application_detail', name="applications_detail"),
  url(r'^applications/(?P<app_id>\d+)/save/$', 'application_save', name="applications_save"),
  url(r'^applications/answer/$', 'application_answer', name="applications_answer"),
  url(r'^applications/(?P<app_id>\d+)/submit/$', 'application_submit', name="applications_submit"),
)


### EVALUATIONS
urlpatterns += patterns('volunteering.views.evaluations',
  url(r'^evaluations/session/(?P<session_id>\d+)/bulkedit/$', 'evaluation_bulkedit', name="evaluation_bulkedit"),
  url(r'^evaluations/session/(?P<session_id>\d+)/emailform/$', 'evaluation_emailform', name="evaluation_emailform"),
  url(r'^evaluations/session/(?P<session_id>\d+)/emailpreview/$', 'evaluation_emailpreview', name="evaluation_emailpreview"),
  url(r'^evaluations/session/(?P<session_id>\d+)/emailsend/$', 'evaluation_emailsend', name="evaluation_emailsend"),
  url(r'^evaluations/session/(?P<session_id>\d+)/$', 'evaluation_list', name="evaluation_list"),
  url(r'^evaluations/(?P<app_id>\d+)/$', 'evaluation_detail', name="evaluation_detail"),
  url(r'^evaluations/(?P<app_id>\d+)/comment/$', 'evaluation_comment', name="evaluation_comment"),
  url(r'^evaluations/(?P<app_id>\d+)/intanswer/$', 'evaluation_interview_answer', name="evaluation_interview_answer"),
  url(r'^evaluations/(?P<app_id>\d+)/criteria/(?P<criteria_id>\d+)/$', 'evaluation_criteria', name="evaluation_criteria"),
)


### PLACEMENTS AND TRACKING
urlpatterns += patterns('volunteering.views.placements',
  url(r'^placements/$', 'placements', name="placements"),
  url(r'^placements/(?P<placement_id>\d+)/$', 'detail', name="placement_detail"),
  url(r'^placements/new/$', 'new', name="placement_new"),
)

"""
urlpatterns += patterns('',
  url(r'^sectors/$', list_detail.object_list, sector_info, name="sectors"),
  url(r'^sectors/(?P<object_id>\d+)/$', create_update.update_object, sector_info_edit, name="sector_detail"),
  url(r'^sectors/new$', create_update.create_object, sector_info_new, name="sector_new"),
)

urlpatterns += patterns('',
  url(r'^travelsegments/$', list_detail.object_list, travelsegment_info, name="travelsegments"),
  url(r'^travelsegments/(?P<object_id>\d+)/$', create_update.update_object, travelsegment_info_edit, name="travelsegment_detail"),
  url(r'^travelsegments/new$', create_update.create_object, travelsegment_info_new, name="travelsegment_new"),
)

urlpatterns += patterns('',
  url(r'^insuranceinstances/$', list_detail.object_list, insuranceinstance_info, name="insuranceinstances"),
  url(r'^insuranceinstances/(?P<object_id>\d+)/$', create_update.update_object, insuranceinstance_info_edit, name="insuranceinstance_detail"),
  url(r'^insuranceinstances/new$', create_update.create_object, insuranceinstance_info_new, name="insuranceinstance_new"),
)

urlpatterns += patterns('',
  url(r'^stipends/$', list_detail.object_list, stipend_info, name="stipends"),
  url(r'^stipends/(?P<object_id>\d+)/$', create_update.update_object, stipend_info_edit, name="stipend_detail"),
  url(r'^stipends/new$', create_update.create_object, stipend_info_new, name="stipend_new"),
)
"""
