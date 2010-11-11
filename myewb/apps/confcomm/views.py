# Create your views here.

import re

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse, \
        HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import simplejson as json

from mailer import send_mail
from avatar.views import change as change_avatar
from account_extra.forms import EmailLoginForm

from confcomm.models import ConferenceProfile, AFRICA_ROLE_CHOICES, \
        AFRICA_COUNTRY_CHOICES, CHAPTER_CHOICES, CANADA_ROLE_CHOICES, \
        ROLE_CHOICES, ConferenceInvitation, RegistrationHit
from confcomm.forms import ConferenceProfileForm, InvitationForm

URL_RE = re.compile('https?://my.ewb.ca/\S*')

def activate_invitation(code):
    try:
        invitation = ConferenceInvitation.objects.get(code=code)
        invitation.activated = True
        invitation.save()
    except:
        pass


def single_page(request):
    """
    The single initial page for AJAX version.
    """
    if 'i' in request.GET:
        activate_invitation(request.GET['i'])
        return HttpResponseRedirect(reverse('confcomm_app'))
    # permission to modify cohort membership of others
    kohort_king = False
    if request.user and request.user.is_authenticated():
        username = request.user.username
        anon = 0
        kohort_king = request.user.has_perm('confcomm.kohort_king')
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
                'kohort_king': json.dumps(kohort_king),
            },
            context_instance=RequestContext(request),
            )

@login_required
def send_invitation(request):
    if request.method == 'POST':
        invitation_form = InvitationForm(request.POST)
        if invitation_form.is_valid():
            data = invitation_form.cleaned_data
            invitation = ConferenceInvitation(
                    sender=ConferenceProfile.objects.get(member_profile__user=invitation_form.sender),
                    receiver=ConferenceProfile.objects.get(member_profile__user=invitation_form.recipient),
                    )
            invitation.save()
            body = data['body']
            matches = URL_RE.findall(body)
            for m in matches:
                url = m.split('?') # split on querystring
                # apologies for the cryptic list comprehension below. it basically splits
                # the qs on &'s and then removes any blank values from trailing &'s or a
                # trailing ? on the url with no other qs components.
                qs = len(url) > 1 and [p for p in url[1].split('&') if p] or [] # split up the querystring into its parts
                qs.append('i=%s' % invitation.code) # add the invitation to the qs
                url = '%s?%s' % (url[0], '&'.join(qs)) # remake the url
                body = body.replace(m, url) # make the replacement in the body
                
            send_mail(subject=data['subject'],
                      txtMessage=body,
                      htmlMessage=None,
                      fromemail=invitation_form.sender_email,
                      recipients=[invitation_form.recipient.email,],
                      use_template=False
                      )
            return HttpResponse('Invitation sent to %s.' % invitation_form.recipient.get_profile().name)
        else:
            return HttpResponseBadRequest('Sending mail failed: %s' % " ".join(["%s: %s." % (k, v) for k, v in invitation_form.errors.items()]))
    else:
        return HttpResponseBadRequest('Sending email requires a POST method')

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
    Record hit and direct user to register for conference.
    """
    if 'i' in request.GET:
        activate_invitation(request.GET['i'])
    hit = RegistrationHit()
    if request.user.is_authenticated():
        hit.user = request.user
    ip = request.META.get('REMOTE_ADDR', None)
    if ip:
        hit.ip_address = ip
    hit.save()
    return HttpResponseRedirect(reverse('confreg'))


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

def login(request):
    form = EmailLoginForm(request.POST)
    if form.login(request):
        response = {
                'username': form.user.username,
                'message': 'Successfully logged in.',
                'success': True,
        }
    else:
        response = {
                'message': 'Your login credentials did not match. Please try again.',
                'success': False,
                'login_name': request.POST['login_name'],
        }
    return HttpResponse(json.dumps(response))

@login_required
def update_avatar(request):
    change_avatar(request, next_override='/')
    return HttpResponse("<textarea>{success: true}</textarea>")

def legacy(request):
    return HttpResponseRedirect(reverse('confcomm_app'))
