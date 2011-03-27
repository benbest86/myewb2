from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.db.models import Q
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext_lazy as _

from jobboard.models import JobPosting
from siteutils.shortcuts import get_object_or_none

def list(request):
    open_jobs = JobPosting.objects.open()
    my_jobs = JobPosting.objects.accepted(request.user)
    my_postings = JobPosting.objects.owned_by(request.user)
    
    # is this necessary? why doesn't autosort do this for me..??
    if request.GET.get('sort', None):
        if request.GET.get('dir', 'desc') == 'asc':
            open_jobs = open_jobs.order_by(request.GET['sort'])
        else:
            open_jobs = open_jobs.order_by('-%s' % request.GET['sort'])
            
    return render_to_response("jobboard/list.html",
                              {"my_postings": my_postings,
                               "my_jobs": my_jobs,
                               "open_jobs": open_jobs},
                              context_instance=RequestContext(request))

def detail(request, id):
    return HttpResponse("not implemented")