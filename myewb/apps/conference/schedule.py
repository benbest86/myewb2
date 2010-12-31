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
from conference.models import ConferenceRegistration, ConferenceCode
from conference.constants import *
from conference.utils import needsToRenew
from networks.models import ChapterInfo
from profiles.models import MemberProfile
from profiles.forms import AddressForm
from siteutils.shortcuts import get_object_or_none
from siteutils.decorators import owner_required, secure_required
from siteutils.helpers import fix_encoding

def schedule(request):
    return HttpResponse("not implemented")

def print_schedule(request):
    return HttpResponse("not implemented")
        
def day(request, day):
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
    

