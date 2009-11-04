from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('volunteering.views',
    url(r'^$', direct_to_template, {"template": "volunteering/volunteering.html"}, name="volunteering_index"),

    url(r'^ov_info/$', "ov_info", name="ov_info"),
    url(r'^assignment/$', "ov_assignment", name="ov_assignment"),
)

urlpatterns += patterns('volunteering.views.placement',
  url(r'^placements/$', "list", name="placement_list"),
  url(r'^placements/page/(?P<page>\d+)$', "list", name="placement_list"),
  url(r'^placements/new$', "new", name="placement_new"),
  url(r'^placements/add$', "add"),
  url(r'^placements/(?P<id>\d+)/edit$', "edit", name="placement_edit"),
  url(r'^placements/(?P<id>\d+)/update$', "update"),
  url(r'^placements/(?P<id>\d+)/delete$', "delete", name="placement_delete"),
)

urlpatterns += patterns('volunteering.views.session',
  url(r'^sessions/$', "list", name="session_list"),
  url(r'^sessions/new$', "new", name="session_new"),
  url(r'^sessions/add$', "add"),
  url(r'^sessions/(?P<id>\d+)/edit$', "edit", name="session_edit"),
  url(r'^sessions/(?P<id>\d+)/update$', "update"),
  url(r'^sessions/(?P<id>\d+)/delete$', "delete", name="session_delete"),
)