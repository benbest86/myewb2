"""myEWB conference scheduling

This file is part of myEWB
Copyright 2009-2010 Engineers Without Borders Canada

@author: Francis Kung
"""

import csv
from datetime import date

from django.contrib import auth
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.contenttypes.models import ContentType
from attachments.models import Attachment

from account_extra.forms import EmailLoginForm, EmailSignupForm

from base_groups.models import BaseGroup
from conference.forms import ConferenceRegistrationForm, ConferenceRegistrationFormPreview, CodeGenerationForm, ConferenceSignupForm
from conference.models import ConferenceRegistration, ConferenceCode, ConferenceRoom, ConferenceSession
from conference.constants import *
from conference.utils import needsToRenew
from networks.models import ChapterInfo
from profiles.models import MemberProfile
from profiles.forms import AddressForm
from siteutils.shortcuts import get_object_or_none
from siteutils.decorators import owner_required, secure_required
from siteutils.helpers import fix_encoding

def schedule(request):
    if request.user.is_authenticated:
        return schedule_for_user(request, request.user)

    if date.today() == date(year=2011, month=1, day=15): #saturday
        return HttpResponseRedirect(reverse('conference_by_day', kwargs={'day': 'sat'}));
    else:
        return HttpResponseRedirect(reverse('conference_by_day', kwargs={'day': 'fri'}));

def schedule_for_user(request, user, day=None, time=None):
    if not day and date.today() == date(year=2011, month=1, day=13): #thurs
        day = 'thurs'
    elif not day and date.today() == date(year=2011, month=1, day=14):
        day = 'fri'
    elif not day and date.today() == date(year=2011, month=1, day=15):
        day = 'sat'

    if day == 'thurs':
        day = date(year=2011, month=1, day=13)
    elif day == 'fri':
        day = date(year=2011, month=1, day=14)
    elif day == 'sat':
        day = date(year=2011, month=1, day=15)

    if day:
        sessions = ConferenceSession.objects.filter(user=user, day=day)
    else:
        sessions = ConferenceSession.objects.filter(user=user)
    
    return render_to_response("conference/schedule/user.html",
                              {"sessions": sessions},
                              context_instance = RequestContext(request))

def schedule_for_user(request, user):
    return HttpResponse("not implemented")

def print_schedule(request):
    return HttpResponse("not implemented")
        
def day(request, day):
    return HttpResponse("not implemented")

def time(request, day, time):
    return HttpResponse("not implemented")

def room(request, room):
    return HttpResponse("not implemented")

def stream(request, stream):
    return HttpResponse("not implemented")

def session_detail(request, session):
    return HttpResponse("not implemented")

def session_new(request):
    return HttpResponse("not implemented")

def session_edit(request, session):
    return HttpResponse("not implemented")

def session_delete(request, session):
    return HttpResponse("not implemented")

def session_rsvp(request):
    return HttpResponse("not implemented")
    
def block(request):
    return HttpResponse("not implemented")
    

