from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from django.http import HttpResponse

urlpatterns = patterns('django.views.generic.simple',
    url(r'^ModifyListMembership/(?P<group_id>\d+)$', 'redirect_to', {'url': reverse('topic_feed_all'),
                                    'permanent': True}),
    )

urlpatterns += patterns('legacy_urls.actions',
    url(r'^DoSilentMainListSignup/(?P<email>[\w\.-_@:\+]+)$', 'silent_signup'),
    )

def silent_signup(request, email):
    User.extras.create_bulk_user(email)
    return HttpResponse("") 
