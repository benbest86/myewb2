from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('volunteering.views',
    url(r'^$', direct_to_template, {"template": "volunteering/volunteering.html"}, name="volunteering_index"),
    url(r'^placements/$', "placement_index", name="placement_index"),
    url(r'^placements/new$', "placement_new", name="placement_new"),
    (r'^placements/(?P<placement_id>\d+)/$', "placement_detail"),

    url(r'^sessions/$', "session_index", name="session_index"),
    (r'^sessions/(?P<session_id>\d+)/$', "session_detail"),

    url(r'^ov_info/$', "ov_info", name="ov_info"),
    url(r'^assignment/$', "ov_assignment", name="ov_assignment"),
)
