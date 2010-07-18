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
"""
application_info = {
  'queryset': Application.objects.all(),
  'template_name': 'volunteering/application/list.html',
  'template_object_name': 'application',
  'paginate_by': 10,
}

application_info_edit = {
  'template_name': 'volunteering/application/form.html',
  'template_object_name': 'application',
  'form_class':  ApplicationForm,
}

application_info_new = {
  'template_name': 'volunteering/application/form.html',
  'form_class':  ApplicationForm,
  'post_save_redirect': '/volunteering/applications/',
}

urlpatterns += patterns('',
  url(r'^applications/$', list_detail.object_list, application_info, name="applications"),
  url(r'^applications/(?P<object_id>\d+)/$', create_update.update_object, application_info_edit, name="application_detail"),
  url(r'^applications/new$', create_update.create_object, application_info_new, name="application_new"),
)
"""

urlpatterns += patterns('volunteering.views.applications',
  url(r'^applications/$', 'applications', name="applications"),
  url(r'^applications/new/(?P<session_id>\d+)/$', 'application_new', name="applications_new"),
  url(r'^applications/(?P<app_id>\d+)/$', 'application_edit', name="applications_edit"),
  url(r'^applications/(?P<app_id>\d+)/save/$', 'application_save', name="applications_save"),
  url(r'^applications/answer/$', 'application_answer', name="applications_answer"),
  url(r'^applications/(?P<app_id>\d+)/submit/$', 'application_submit', name="applications_submit"),
)

answer_info = {
  'queryset': Answer.objects.all(),
  'template_name': 'volunteering/answer/list.html',
  'template_object_name': 'answer',
  'paginate_by': 10,
}

answer_info_edit = {
  'template_name': 'volunteering/answer/form.html',
  'template_object_name': 'answer',
  'form_class':  AnswerForm,
}

answer_info_new = {
  'template_name': 'volunteering/answer/form.html',
  'form_class':  AnswerForm,
  'post_save_redirect': '/volunteering/answers/',
}

urlpatterns += patterns('',
  url(r'^answers/$', list_detail.object_list, answer_info, name="answers"),
  url(r'^answers/(?P<object_id>\d+)/$', create_update.update_object, answer_info_edit, name="answer_detail"),
  url(r'^answers/new$', create_update.create_object, answer_info_new, name="answer_new"),
)

### EVALUATIONS

evaluationresponse_info = {
  'queryset': EvaluationResponse.objects.all(),
  'template_name': 'volunteering/evaluationresponse/list.html',
  'template_object_name': 'evaluationresponse',
  'paginate_by': 10,
}

evaluationresponse_info_edit = {
  'template_name': 'volunteering/evaluationresponse/form.html',
  'template_object_name': 'evaluationresponse',
  'form_class':  EvaluationResponseForm,
}

evaluationresponse_info_new = {
  'template_name': 'volunteering/evaluationresponse/form.html',
  'form_class':  EvaluationResponseForm,
  'post_save_redirect': '/volunteering/evaluationresponses/',
}

urlpatterns += patterns('',
  url(r'^evaluationresponses/$', list_detail.object_list, evaluationresponse_info, name="evaluationresponses"),
  url(r'^evaluationresponses/(?P<object_id>\d+)/$', create_update.update_object, evaluationresponse_info_edit, name="evaluationresponse_detail"),
  url(r'^evaluationresponses/new$', create_update.create_object, evaluationresponse_info_new, name="evaluationresponse_new"),
)

evaluation_info = {
  'queryset': Evaluation.objects.all(),
  'template_name': 'volunteering/evaluation/list.html',
  'template_object_name': 'evaluation',
  'paginate_by': 10,
}

evaluation_info_edit = {
  'template_name': 'volunteering/evaluation/form.html',
  'template_object_name': 'evaluation',
  'form_class':  EvaluationForm,
}

evaluation_info_new = {
  'template_name': 'volunteering/evaluation/form.html',
  'form_class':  EvaluationForm,
  'post_save_redirect': '/volunteering/evaluations/',
}

urlpatterns += patterns('',
  url(r'^evaluations/$', list_detail.object_list, evaluation_info, name="evaluations"),
  url(r'^evaluations/(?P<object_id>\d+)/$', create_update.update_object, evaluation_info_edit, name="evaluation_detail"),
  url(r'^evaluations/new$', create_update.create_object, evaluation_info_new, name="evaluation_new"),
)


### PLACEMENTS AND TRACKING

def placements_all(request):
  return placements_by_type(request, "all")

def placements_by_type(request, placement_type):
  from django.db.models import Q
  import datetime

  if placement_type == "past":
    placement_list = Placement.objects.select_related().filter(end_date__lt=datetime.date.today())
  elif placement_type == "active":
    placement_list = Placement.objects.select_related().filter(Q(start_date__isnull=False) & Q(start_date__lte=datetime.date.today()) & (Q(end_date__gte=datetime.date.today()) | Q(end_date__isnull=True)))
  else:
    placement_list = Placement.objects.select_related()
  
  sector_list = [['', '------']] + [[sector.id, sector.abbreviation] for sector in Sector.objects.all()]
  country_list = (('', '------'),) + EWB_PLACEMENTS
  sending_group_list = [['', '------']] + [[sg.id, sg] for sg in SendingGroup.objects.all()]
  
  selected_sector = request.GET.get("sector", None)
  selected_country = request.GET.get("country", None)
  selected_sending_group = request.GET.get("sending_group", None)
  
  if selected_sector:
    placement_list = placement_list.filter(sector=selected_sector)

  if selected_country:
    placement_list = placement_list.filter(country=selected_country)

  if selected_sending_group:
    placement_list = placement_list.filter(profile__sending_groups=selected_sending_group)

  response = list_detail.object_list(request,
          queryset=placement_list,
          template_name="volunteering/placement/list.html",
          template_object_name="placement",
          extra_context= { "base_url": reverse("placements"),
                             "type": placement_type,
                             "selected_sending_group": selected_sending_group,
                             "sending_group_list": sending_group_list,
                             "selected_country": selected_country,
                             "country_list": country_list,
                             "selected_sector": selected_sector,
                             "sector_list": sector_list,
                             "page_list": [{"label":"All placements", "url":"all"},
                                            {"label":"Active placements", "url":"active"},
                                            {"label":"Past placements", "url":"past"}],
                                          },
          )
  
  return response

placement_info = {
  'queryset': Placement.objects.all(),
  'template_name': 'volunteering/placement/list.html',
  'template_object_name': 'placement',
  'paginate_by': 10,
  
}

placement_info_edit = {
  'template_name': 'volunteering/placement/form.html',
  'template_object_name': 'placement',
  'form_class':  PlacementForm,
}

placement_info_new = {
  'template_name': 'volunteering/placement/form.html',
  'form_class':  PlacementForm,
  'post_save_redirect': '/volunteering/placements/',
}

urlpatterns += patterns('',
  url(r'^placements/$', placements_all, name="placements"),
  url(r'^placements/(?P<placement_type>(all|active|past))/$', placements_by_type),
  url(r'^placements/(?P<object_id>\d+)/$', create_update.update_object, placement_info_edit, name="placement_detail"),
  url(r'^placements/new$', create_update.create_object, placement_info_new, name="placement_new"),
)

sector_info = {
  'queryset': Sector.objects.all(),
  'template_name': 'volunteering/sector/list.html',
  'template_object_name': 'sector',
  'paginate_by': 10,
}

sector_info_edit = {
  'template_name': 'volunteering/sector/form.html',
  'template_object_name': 'sector',
  'form_class':  SectorForm,
}

sector_info_new = {
  'template_name': 'volunteering/sector/form.html',
  'form_class':  SectorForm,
  'post_save_redirect': '/volunteering/sectors/',
}

urlpatterns += patterns('',
  url(r'^sectors/$', list_detail.object_list, sector_info, name="sectors"),
  url(r'^sectors/(?P<object_id>\d+)/$', create_update.update_object, sector_info_edit, name="sector_detail"),
  url(r'^sectors/new$', create_update.create_object, sector_info_new, name="sector_new"),
)

travelsegment_info = {
  'queryset': TravelSegment.objects.all(),
  'template_name': 'volunteering/travelsegment/list.html',
  'template_object_name': 'travelsegment',
  'paginate_by': 10,
}

travelsegment_info_edit = {
  'template_name': 'volunteering/travelsegment/form.html',
  'template_object_name': 'travelsegment',
  'form_class':  TravelSegmentForm,
}

travelsegment_info_new = {
  'template_name': 'volunteering/travelsegment/form.html',
  'form_class':  TravelSegmentForm,
  'post_save_redirect': '/volunteering/travelsegments/',
}

urlpatterns += patterns('',
  url(r'^travelsegments/$', list_detail.object_list, travelsegment_info, name="travelsegments"),
  url(r'^travelsegments/(?P<object_id>\d+)/$', create_update.update_object, travelsegment_info_edit, name="travelsegment_detail"),
  url(r'^travelsegments/new$', create_update.create_object, travelsegment_info_new, name="travelsegment_new"),
)

insuranceinstance_info = {
  'queryset': InsuranceInstance.objects.all(),
  'template_name': 'volunteering/insuranceinstance/list.html',
  'template_object_name': 'insuranceinstance',
  'paginate_by': 10,
}

insuranceinstance_info_edit = {
  'template_name': 'volunteering/insuranceinstance/form.html',
  'template_object_name': 'insuranceinstance',
  'form_class': InsuranceInstanceForm,
}

insuranceinstance_info_new = {
  'template_name': 'volunteering/insuranceinstance/form.html',
  'form_class': InsuranceInstanceForm,
  'post_save_redirect': '/volunteering/insuranceinstances/',
}

urlpatterns += patterns('',
  url(r'^insuranceinstances/$', list_detail.object_list, insuranceinstance_info, name="insuranceinstances"),
  url(r'^insuranceinstances/(?P<object_id>\d+)/$', create_update.update_object, insuranceinstance_info_edit, name="insuranceinstance_detail"),
  url(r'^insuranceinstances/new$', create_update.create_object, insuranceinstance_info_new, name="insuranceinstance_new"),
)


stipend_info = {
  'queryset': Stipend.objects.all(),
  'template_name': 'volunteering/stipend/list.html',
  'template_object_name': 'stipend',
  'paginate_by': 10,
}

stipend_info_edit = {
  'template_name': 'volunteering/stipend/form.html',
  'template_object_name': 'stipend',
  'form_class':  StipendForm,
}

stipend_info_new = {
  'template_name': 'volunteering/stipend/form.html',
  'form_class':  StipendForm,
  'post_save_redirect': '/volunteering/stipends/',
}

urlpatterns += patterns('',
  url(r'^stipends/$', list_detail.object_list, stipend_info, name="stipends"),
  url(r'^stipends/(?P<object_id>\d+)/$', create_update.update_object, stipend_info_edit, name="stipend_detail"),
  url(r'^stipends/new$', create_update.create_object, stipend_info_new, name="stipend_new"),
)


sendinggroup_info = {
  'queryset': SendingGroup.objects.all(),
  'template_name': 'volunteering/sendinggroup/list.html',
  'template_object_name': 'sendinggroup',
  'paginate_by': 10,
}

sendinggroup_info_edit = {
  'template_name': 'volunteering/sendinggroup/form.html',
  'template_object_name': 'sendinggroup',
  'form_class':  SendingGroupForm,
}

sendinggroup_info_new = {
  'template_name': 'volunteering/sendinggroup/form.html',
  'form_class':  SendingGroupForm,
  'post_save_redirect': '/volunteering/sendinggroups/',
}

def sendinggroup_members(request, object_id):
  sending_group = SendingGroup.objects.get(id=object_id)
  group_members = MemberProfile.objects.filter(sending_groups=sending_group)
  non_group_members = MemberProfile.objects.exclude(sending_groups=sending_group)
  
  response = render_to_response("volunteering/sendinggroup/members.html",
           { 
             "sending_group": sending_group,
             "group_members": group_members,
             "non_members": [[member.id, member.name] for member in non_group_members],
             "selected_member": None,
          },
          context_instance=RequestContext(request)
          )
  
  return response

urlpatterns += patterns('',
  url(r'^sendinggroups/$', list_detail.object_list, sendinggroup_info, name="sendinggroups"),
  url(r'^sendinggroups/(?P<object_id>\d+)/$', create_update.update_object, sendinggroup_info_edit, name="sendinggroup_detail"),
  url(r'^sendinggroups/new$', create_update.create_object, sendinggroup_info_new, name="sendinggroup_new"),
  url(r'^sendinggroups/members/(?P<object_id>\d+)$', sendinggroup_members, name="sendinggroup_members"),

)
