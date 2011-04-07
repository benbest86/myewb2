from django.conf.urls.defaults import *
from django.http import HttpResponseRedirect

urlpatterns = patterns('legacy_urls.volunteering',
    url(r'^(.*)$', 'redirect')
    )

def redirect(request, path):
    path = request.path
    path = path.replace('volunteering/', 'apply/', 1)
    print path
    return HttpResponseRedirect(path)