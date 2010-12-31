"""myEWB conference scheduling

This file is part of myEWB
Copyright 2009-2010 Engineers Without Borders Canada

@author: Francis Kung
"""

import csv, datetime
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
from conference.forms import ConferenceSessionForm
from conference.models import ConferenceRegistration, ConferenceCode, ConferenceRoom, ConferenceSession, STREAMS
from conference.constants import *
from conference.utils import needsToRenew
from networks.models import ChapterInfo
from profiles.models import MemberProfile
from profiles.forms import AddressForm
from siteutils.shortcuts import get_object_or_none
from siteutils.decorators import owner_required, secure_required
from siteutils.helpers import fix_encoding

CONFERENCE_DAYS = (('thurs', 'Thursday', 13),
                   ('fri', 'Friday', 14),
                   ('sat', 'Saturday', 15))

def schedule(request):
    if request.user.is_authenticated:
        if ConferenceSession.objects.filter(attendees=request.user).count():
            return HttpResponseRedirect(reverse('conference_for_user'));

    if date.today() == date(year=2011, month=1, day=15): #saturday
        return HttpResponseRedirect(reverse('conference_by_day', kwargs={'day': 'sat', 'stream': 'all'}));
    else:
        return HttpResponseRedirect(reverse('conference_by_day', kwargs={'day': 'fri', 'stream': 'all'}));

@login_required
def schedule_for_user(request, user=None, day=None, time=None):
    if not user:
        user = request.user
        
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
        sessions = ConferenceSession.objects.filter(attendees=user, day=day)
    else:
        sessions = ConferenceSession.objects.filter(attendees=user)
    
    timelist = []
    for t in range(8, 22):
        timelist.append(t)

    return render_to_response("conference/schedule/user.html",
                              {"sessions": sessions,
                               "day": day,
                               "timelist": timelist,
                               "days": CONFERENCE_DAYS},
                              context_instance = RequestContext(request))


@login_required
def print_schedule(request):
    return HttpResponse("not implemented")
        
def day(request, day, stream):
    if day == 'thurs':
        fday = date(year=2011, month=1, day=13)
    elif day == 'fri':
        fday = date(year=2011, month=1, day=14)
    elif day == 'sat':
        fday = date(year=2011, month=1, day=15)
    else:                       # use fri as a default for unrecognized days
        fday = date(year=2011, month=1, day=14)
        
    timelist = []
    for t in range(8, 22):
        timelist.append(t)

    sessions = ConferenceSession.objects.filter(day=fday)
    if stream != 'all':
        sessions = sessions.filter(stream=stream)
    
    return render_to_response("conference/schedule/day.html",
                              {"sessions": sessions,
                               "day": day,
                               "timelist": timelist,
                               "stream": stream,
                               "streams": STREAMS,
                               "days": CONFERENCE_DAYS},
                              context_instance = RequestContext(request))

def time(request, day, time):
    if day == 'thurs':
        fday = date(year=2011, month=1, day=13)
    elif day == 'fri':
        fday = date(year=2011, month=1, day=14)
    elif day == 'sat':
        fday = date(year=2011, month=1, day=15)
    else:                       # use fri as a default for unrecognized days
        fday = date(year=2011, month=1, day=14)

    ftime = datetime.time(hour=int(time[0:2]), minute=int(time[2:4]))
    sessions = ConferenceSession.objects.filter(day=fday, time=ftime)
    
    return render_to_response("conference/schedule/time.html",
                              {"sessions": sessions,
                               "day": fday,
                               "time": ftime},
                              context_instance = RequestContext(request))

def stream(request, stream):
    sessions = ConferenceSession.objects.filter(stream=stream)
    
    return render_to_response("conference/schedule/time.html",
                              {"sessions": sessions,
                               "stream": stream,
                               "streams": STREAMS},
                              context_instance = RequestContext(request))

def room(request, room):
    return HttpResponse("not implemented")

def session_detail(request, session):
    s = get_object_or_404(ConferenceSession, id=session)
    
    # TODO: build RSVP list, predict capacity...
    
    return render_to_response("conference/schedule/session_detail.html",
                              {"session": s},
                              context_instance = RequestContext(request))


@login_required
def session_new(request):
    if not request.user.has_module_perms("conference"):
        return HttpResponseRedirect(reverse('conference_schedule'))

    if request.method == 'POST':
        form = ConferenceSessionForm(request.POST)

        if form.is_valid():
            session = form.save()
            return HttpResponseRedirect(reverse('conference_session', kwargs={'session': session.id}))
    else:
        form = ConferenceSessionForm()
        
    return render_to_response("conference/schedule/session_edit.html",
                              {"form": form,
                               "new": True},
                              context_instance = RequestContext(request))

@login_required
def session_edit(request, session):
    if not request.user.has_module_perms("conference"):
        return HttpResponseRedirect(reverse('conference_schedule'))

    s = get_object_or_404(ConferenceSession, id=session)
    
    if request.method == 'POST':
        form = ConferenceSessionForm(request.POST, instance=s)

        if form.is_valid():
            session = form.save()
            return HttpResponseRedirect(reverse('conference_session', kwargs={'session': session.id}))
    else:
        form = ConferenceSessionForm(instance=s)
        
    return render_to_response("conference/schedule/session_edit.html",
                              {"form": form},
                              context_instance = RequestContext(request))

@login_required
def session_delete(request, session):
    if not request.user.has_module_perms("conference"):
        return HttpResponseRedirect(reverse('conference_schedule'))

    s = get_object_or_404(ConferenceSession, id=session)
    
    if request.method == 'POST' and request.POST.get('delete', None):
        redirect_day = 14
        if s.day.day == 13:
            redirect_day = 13
        elif s.day.day == 15:
            redirect_day = 15
            
        s.delete()
        return HttpResponseRedirect(reverse('conference_by_day', kwargs={'day': redirect_day}))
        
    return render_to_response("conference/schedule/session_delete.html",
                              {"session": s},
                              context_instance = RequestContext(request))

@login_required
def session_attend(request, session):
    s = get_object_or_404(ConferenceSession, id=session)
    s.maybes.remove(request.user)
    s.attendees.add(request.user)
    
    return HttpResponseRedirect(reverse('conference_session', kwargs={'session': s.id}))
    
@login_required
def session_tentative(request, session):
    s = get_object_or_404(ConferenceSession, id=session)
    s.attendees.remove(request.user)
    s.maybes.add(request.user)
    
    return HttpResponseRedirect(reverse('conference_session', kwargs={'session': s.id}))
    
    
@login_required
def session_skip(request, session):
    s = get_object_or_404(ConferenceSession, id=session)
    s.attendees.remove(request.user)
    s.maybes.remove(request.user)
    
    return HttpResponseRedirect(reverse('conference_session', kwargs={'session': s.id}))
    
@login_required
def block(request):
    return HttpResponse("not implemented")
    

