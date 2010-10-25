# Create your views here.

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from confcomm.models import ConferenceProfile

def index(request):
    """
    Main landing page for the conference community.
    """
    user = request.user
    # assume all registered conference goers have a ConferenceProfile object
    if not user.is_authenticated() or ConferenceProfile.objects.filter(member_profile__user=user).count() != 1:
        return HttpResponseRedirect(reverse('confcomm_register'))
    return render_to_response('confcomm/index.html',
            {},
            context_instance=RequestContext(request)
            )

def register(request):
    """
    Direct user to register for conference.
    """
    return render_to_response('confcomm/register.html',
            {},
            context_instance=RequestContext(request)
            )
