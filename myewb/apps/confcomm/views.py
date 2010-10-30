# Create your views here.

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import simplejson as json

from confcomm.models import ConferenceProfile, AFRICA_ROLE_CHOICES, \
        AFRICA_COUNTRY_CHOICES, CHAPTER_CHOICES, CANADA_ROLE_CHOICES, \
        ROLE_CHOICES
from confcomm.forms import ConferenceProfileForm

def single_page(request):
    """
    The single initial page for AJAX version.
    """
    if request.user and request.user.is_authenticated():
        username = request.user.username
        anon = 0
    else:
        username = ""
        anon = 1
    return render_to_response('confcomm/single.html',
            {
                'username': username,
                'anon': anon,
                'countries_list': json.dumps(AFRICA_COUNTRY_CHOICES),
                'chapters_list': json.dumps(CHAPTER_CHOICES),
                'canada_roles_list': json.dumps(CANADA_ROLE_CHOICES),
                'africa_roles_list': json.dumps(AFRICA_ROLE_CHOICES),
                'years_list': json.dumps([(y, y) for y in range(2001, 2011)]),
                'roles_list': json.dumps(ROLE_CHOICES),
            },
            context_instance=RequestContext(request),
            )

def index(request):
    """
    Main landing page for the conference community.
    """
    return render_to_response('confcomm/index.html',
            {},
            context_instance=RequestContext(request),
            )

def register(request):
    """
    Direct user to register for conference.
    """
    return render_to_response(
            'confcomm/register.html',
            {},
            context_instance=RequestContext(request),)

def profile(request, username=None):
    """
    View for viewing a profile.
    """
    # boolean for whether or not current user owns the profile
    is_owner = False
    user = request.user
    if not user.is_authenticated():
        is_owner = False
        if username is None:
            return Http404
    else:
        if username is None:
            username = user.username
            is_owner = True
        elif username == user.username:
            is_owner = True
    profile = get_object_or_404(ConferenceProfile, member_profile__user__username=username)


    return render_to_response('confcomm/profile.html',
            {
                'profile': profile,
                'is_owner': is_owner,
            },
            context_instance=RequestContext(request),)

@login_required
def profile_edit(request):
    user = request.user
    profile = get_object_or_404(ConferenceProfile, member_profile__user=user)
    if request.method == 'POST':
        form = ConferenceProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save()
            return HttpResponseRedirect(reverse('confcomm_profile'))
    else:
        form = ConferenceProfileForm(instance=profile)
    return render_to_response('confcomm/edit_profile.html',
            {'form':form},
            context_instance=RequestContext(request),)
