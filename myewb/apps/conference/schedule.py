"""myEWB conference scheduling

This file is part of myEWB
Copyright 2009-2010 Engineers Without Borders Canada

@author: Francis Kung
"""

import datetime, settings
from datetime import date

from account.models import PasswordReset
from django.contrib import auth
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.auth.views import logout as pinaxlogout
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from pinax.apps.account.forms import ResetPasswordKeyForm, ResetPasswordForm

from account_extra.forms import EmailLoginForm
from base_groups.models import BaseGroup
from conference.forms import ConferenceSessionForm, ConferencePrivateEventForm
from conference.models import ConferenceRegistration, ConferenceSession, ConferencePrivateEvent, STREAMS, STREAMS_SHORT
from mailer.sendmail import send_mail
from siteutils import online_middleware
from siteutils.shortcuts import get_object_or_none
from siteutils.helpers import fix_encoding

CONFERENCE_DAYS = (('thurs', 'Thursday', 13),
                   ('fri', 'Friday', 14),
                   ('sat', 'Saturday', 15))

def schedule(request):
    if request.user.is_authenticated():
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
        
    if not day and date.today() == date(year=2011, month=1, day=13): #thur
        day = 'thurs'
    elif not day and date.today() == date(year=2011, month=1, day=14):
        day = 'fri'
    elif not day and date.today() == date(year=2011, month=1, day=15):
        day = 'sat'
    elif not day:
        day = 'fri'

    if day == 'thurs':
        fday = date(year=2011, month=1, day=13)
    elif day == 'fri':
        fday = date(year=2011, month=1, day=14)
    elif day == 'sat':
        fday = date(year=2011, month=1, day=15)

    query = Q(attendees = user) | Q(stream='common')
    if day:
        sessions = ConferenceSession.objects.filter(query, day=fday)
        private = ConferencePrivateEvent.objects.filter(creator=request.user, day=fday)
    else:
        sessions = ConferenceSession.objects.filter(query)
        private = ConferencePrivateEvent.objects.filter(creator=request.user)
        
    user_sessions = list(sessions)
    user_sessions.extend(private)

    timelist = []
    for t in range(8, 22):
        timelist.append(t)

    return render_to_response("conference/schedule/user.html",
                              {"sessions": user_sessions,
                               "day": day,
                               "fday": fday,
                               "timelist": timelist,
                               "days": CONFERENCE_DAYS,
                               "printable": request.GET.get('printable', None)},
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
        sessions = sessions.filter(Q(stream=stream) | Q(stream='common'))
    
    return render_to_response("conference/schedule/day.html",
                              {"sessions": sessions,
                               "day": day,
                               "timelist": timelist,
                               "stream": stream,
                               "streams": STREAMS_SHORT,
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
                               "dayshort": day,
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
    
    attendees = s.attendees.order_by('?')
    numattendees = attendees.count()

    if request.is_mobile or not request.user.has_module_perms("conference"):
        if  numattendees < 10:
            attendees = attendees[0:numattendees]
        else:
            attendees = attendees[0:10]
    
    return render_to_response("conference/schedule/session_detail.html",
                              {"session": s,
                               "attendees": attendees,
                               "numattendees": numattendees},
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
        redirect_day = 'fri'
        if s.day.day == 13:
            redirect_day = 'thurs'
        elif s.day.day == 15:
            redirect_day = 'sat'
            
        s.delete()
        return HttpResponseRedirect(reverse('conference_by_day', kwargs={'day': redirect_day, 'stream': 'all'}))
        
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
def private_detail(request, session):
    s = get_object_or_404(ConferencePrivateEvent, id=session)
    
    if s.creator != request.user:
        return render_to_response("conference/schedule/denied.html",
                                  {}, context_instance = RequestContext(request))
    
    return render_to_response("conference/schedule/session_private_detail.html",
                              {"session": s,
                               "attendees": [],
                               "private": True},
                              context_instance = RequestContext(request))

@login_required
def private_new(request):
    if request.method == 'POST':
        form = ConferencePrivateEventForm(request.POST)

        if form.is_valid():
            session = form.save(commit=False)
            session.creator = request.user
            session.save()
            return HttpResponseRedirect(reverse('conference_private', kwargs={'session': session.id}))
    else:
        form = ConferencePrivateEventForm()
        
    return render_to_response("conference/schedule/session_edit.html",
                              {"form": form,
                               "new": True,
                               "private": True},
                              context_instance = RequestContext(request))

@login_required
def private_edit(request, session):
    s = get_object_or_404(ConferencePrivateEvent, id=session)
    
    if s.creator != request.user:
        return render_to_response("conference/schedule/denied.html",
                                  {}, context_instance = RequestContext(request))
    
    if request.method == 'POST':
        form = ConferencePrivateEventForm(request.POST, instance=s)

        if form.is_valid():
            session = form.save()
            return HttpResponseRedirect(reverse('conference_private', kwargs={'session': session.id}))
    else:
        form = ConferencePrivateEventForm(instance=s)
        
    return render_to_response("conference/schedule/session_edit.html",
                              {"form": form,
                               "private": True},
                              context_instance = RequestContext(request))

@login_required
def private_delete(request, session):
    s = get_object_or_404(ConferencePrivateEvent, id=session)
    
    if s.creator != request.user:
        return render_to_response("conference/schedule/denied.html",
                                  {}, context_instance = RequestContext(request))
    
    if request.method == 'POST' and request.POST.get('delete', None):
        redirect_day = 14
        if s.day.day == 13:
            redirect_day = 13
        elif s.day.day == 15:
            redirect_day = 15
            
        s.delete()
        return HttpResponseRedirect(reverse('conference_for_user'))
        
    return render_to_response("conference/schedule/session_delete.html",
                              {"session": s,
                               "private": True},
                              context_instance = RequestContext(request))

def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('conference_schedule'))

    signin_form = EmailLoginForm(initial={'remember': 'on'})
    
    if request.method == "POST":
        signin_form = EmailLoginForm(request.POST)
        if signin_form.is_valid():
            user = signin_form.user
            auth.login(request, user)
            return HttpResponseRedirect(reverse('conference_schedule'))

    return render_to_response("conference/schedule/login.html",
                              {'form': signin_form},
                              context_instance = RequestContext(request))

def logout(request):
    online_middleware.remove_user(request)
    return pinaxlogout(request, next_page=reverse('conference_schedule'))

def reset_password(request, key=None):
    context = {}
    
    if request.method == 'POST' and request.POST.get('email', None):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('conference_schedule'))
            
        email = request.POST.get('email', None)
        if User.objects.filter(email__iexact=email).count():
            context['email'] = email
        else:
            context['email_error'] = email

        for user in User.objects.filter(email__iexact=email):
            temp_key = sha_constructor("%s%s%s" % (
                settings.SECRET_KEY,
                user.email,
                settings.SECRET_KEY,
            )).hexdigest()

            # save it to the password reset model
            password_reset = PasswordReset(user=user, temp_key=temp_key)
            password_reset.save()

            current_site = Site.objects.get_current()
            domain = unicode(current_site.domain)

            #send the password reset email
            subject = "myEWB password reset"
            message = render_to_string("conference/schedule/password_reset_message.txt", {
                "user": user,
                "temp_key": temp_key,
                "domain": domain,
            })
            send_mail(subject=subject, txtMessage=message,
                      fromemail=settings.DEFAULT_FROM_EMAIL,
                      recipients=[user.email], priority="high")
        
    elif key:
        if PasswordReset.objects.filter(temp_key__exact=key, reset=False).count():
            if request.method == 'POST':
                form = ResetPasswordKeyForm(request.POST)
                
                if form.is_valid():
                    # get the password_reset object
                    temp_key = form.cleaned_data.get("temp_key")
                    password_reset = PasswordReset.objects.filter(temp_key__exact=temp_key, reset=False)
                    password_reset = password_reset[0]  # should always be safe, as form_clean checks this

                    # now set the new user password
                    user = User.objects.get(passwordreset__exact=password_reset)
                    result = user.set_password(form.cleaned_data['password1'])

                    if not result:
                        # unsuccessful
                        form._errors[forms.forms.NON_FIELD_ERRORS] = ["Error (password is too simple maybe?)"]
                    else:
                        user.save()

                        # change all the password reset records to this person to be true.
                        for password_reset in PasswordReset.objects.filter(user=user):
                            password_reset.reset = True
                            password_reset.save()

                        user = auth.authenticate(username=user.username, password=form.cleaned_data['password1'])
                        auth.login(request, user)
                        return HttpResponseRedirect(reverse('conference_schedule'))
            else:
                form = ResetPasswordKeyForm(initial={'temp_key': key})
            
            context['keyvalid'] = True
            context['form'] = form
        else:
            context['keyerror'] = True
    
    else:
        return HttpResponseRedirect(reverse('conference_schedule_login'))

    return render_to_response("conference/schedule/reset.html",
                              context,
                              context_instance = RequestContext(request))

