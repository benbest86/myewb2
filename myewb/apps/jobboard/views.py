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
    return HttpResponse("job board")