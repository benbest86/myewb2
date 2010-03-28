
from django.conf.urls.defaults import *

from group_announcements.models import Announcement
from group_announcements.views import *


urlpatterns = patterns("",
    url(r"^(?P<object_id>\d+)/$", announcement_detail, name="announcement_detail"),
    url(r"^new/$", announcement_create, name="announcement_create"),
    url(r"^(?P<object_id>\d+)/hide/$", announcement_hide, name="announcement_hide"),
    url(r"^(?P<object_id>\d+)/delete/$", announcement_delete, name="announcement_delete"),
    url(r"^$", announcement_list, name="announcement_home"),
)
