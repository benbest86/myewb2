"""myEWB conference registration views

This file is part of myEWB
Copyright 2009 Engineers Without Borders Canada

Created on: 2009-10-18
@author: Francis Kung
"""

from django.contrib import auth
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
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

@secure_required
def login(request):
    
    signin_form = EmailLoginForm()
    signup_form = ConferenceSignupForm()
    
    if request.method == "POST" and request.POST.get('action', None):
        if request.POST['action'] == 'signin':
            signin_form = EmailLoginForm(request.POST)
            if signin_form.is_valid():
                user = signin_form.user
                user.is_bulk = False
                user.save()
                auth.login(request, user)
                return HttpResponseRedirect(reverse('confreg'))
        else:
            signup_form = ConferenceSignupForm(request.POST)
            
            if signup_form.is_valid():
                username, password = signup_form.save()
                user = auth.authenticate(username=username, password=password)
                auth.login(request, user)
                
                return HttpResponseRedirect(reverse('confreg'))
        
    return render_to_response('conference/login.html',
                              {"signin_form": signin_form,
                               "signup_form": signup_form},
                              context_instance = RequestContext(request))

@secure_required
#@login_required
def view_registration(request):
    
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('conference_login'))
    
    user = request.user
    
    try:
        # if already registered, we display "thank you" page and offer
        # cancellation or a receipt
        registration = ConferenceRegistration.objects.get(user=user, cancelled=False)
        form = None

        return HttpResponseRedirect(reverse('confcomm_app'))

    except ObjectDoesNotExist:
        # if not registered, we display the registration form
        registration = None

        if request.method == 'POST':
            # or, in this case, process the registration form...
            form = ConferenceRegistrationForm(request.POST)
            form.user = user
            if form.is_valid():
                registration = form.save()
                
        else:
            form = ConferenceRegistrationForm()
            form.user = user
                
    needsRenewal = needsToRenew(request.user.get_profile())

    return render_to_response('conference/registration.html',
                              {'registration': registration,
                               'form': form,
                               'user': request.user,
                               'needsRenewal': needsRenewal
                              },
                              context_instance=RequestContext(request)
                             )
    
@secure_required
@login_required
def registration_preview(request):
#def pay_membership_preview(request, username):
    username = request.user.username
    
    f = ConferenceRegistrationForm(request.POST, request.FILES)
    f.user = request.user
    if f.is_valid():
        if f.cleaned_data.get('resume', None):
            resume = Attachment()
            resume.creator = request.user
            resume.content_type = ContentType.objects.get_for_model(request.user)
            resume.object_id = request.user.id
            resume.attachment_file = f.cleaned_data['resume']
            resume.save()
            
    return ConferenceRegistrationFormPreview(ConferenceRegistrationForm)(request, username=username)
        
@login_required
def receipt(request):

    try:
        registration = ConferenceRegistration.objects.get(user=request.user, cancelled=False)

    except ObjectDoesNotExist:
        #message = loader.get_template("profiles/suggest_network.html")
        #c = Context({'network': network, 'action': 'join'})
        #request.user.message_set.create(message=message.render(c))
        request.user.message_set.create(message="You are not registered")
        
        return HttpResponseRedirect(reverse('confreg'))

    return render_to_response('conference/receipt.html',
                              {'reg': registration},
                              context_instance=RequestContext(request)
                             )
        
@login_required
def cancel(request):
    try:
        registration = ConferenceRegistration.objects.get(user=request.user, cancelled=False)

    except ObjectDoesNotExist:
        #message = loader.get_template("profiles/suggest_network.html")
        #c = Context({'network': network, 'action': 'join'})
        #request.user.message_set.create(message=message.render(c))
        request.user.message_set.create(message="You are not registered")
        
        return HttpResponseRedirect(reverse('confreg'))

    # a post request indicates that they've seen the confirm page...
    if request.method == 'POST':
        registration.cancel()
        registration.save()
        
        # send an email to myself to manually refund the registration fee
        body = "Conference registration cancelled.\n\n"
        body += "Name: " + registration.user.first_name + " " + registration.user.last_name+ "\n"
        body += "Transaction ID: " + registration.txid + "\n"
        body += "Receipt number: " + registration.receiptNum + "\n\n"
        
        body += "Refund amount: %s" % registration.getRefundAmount()
        
        send_mail('Confreg cancelled', body, 'mailer@my.ewb.ca',
                  ['monitoring@ewb.ca'], fail_silently=False)

        cancelled = True
    else:
        cancelled = False
        
    # this template will show a confirm page.
    return render_to_response('conference/cancel.html',
                              {'reg': registration,
                               'cancelled': cancelled},
                               context_instance=RequestContext(request)
                               )
    
@login_required
def list(request, chapter=None):
    if chapter == None:
        
        # would be pretty easy to exnted this to provide listings from
        # any group, not just a chapter.
        chapters = ChapterInfo.objects.all()
        
        if not request.user.has_module_perms('conference'):
            # non-admins: only see chapters you're an exec of
            chapters = chapters.filter(network__members__user=request.user,
                                       network__members__is_admin=True)

        # if only one chapter, display it right away
        if chapters.count() == 1:
            chapter = chapters[0].network.slug

        else:
            # otherwise, show a summary page
            for chapter in chapters:
                registrations = ConferenceRegistration.objects.filter(user__memberprofile__chapter=chapter.network,
                                                                      cancelled=False)
                chapter.numRegistrations = registrations.count()
            
            return render_to_response('conference/select_chapter.html',
                                      {'chapters': chapters},
                                      context_instance=RequestContext(request)
                                      )
    
    # so... by mangling the slug, you *can* actually see listings from all
    # groups you're an admin of! ;-)
    group = get_object_or_404(BaseGroup, slug=chapter)
    
    # permissions chcek!
    if not group.user_is_admin(request.user) and not request.user.has_module_perms('conference'):
        return render_to_response('denied.html', context_instance=RequestContext(request))
        
    registrations = ConferenceRegistration.objects.filter(user__memberprofile__chapter=group,
                                                          cancelled=False)

    return render_to_response('conference/list.html',
                              {'registrations': registrations,
                               'group': group},
                               context_instance=RequestContext(request)
                               )
    
def generate_codes(request):
    # ensure only admins...
    if request.user.has_module_perms('conference'):
        codes = []
    
        if request.method == 'POST':
            form = CodeGenerationForm(request.POST)
        
            if form.is_valid():
                start = form.cleaned_data['start'] 
                number = form.cleaned_data['number']
                type  = form.cleaned_data['type']
            
                # iterate through request codes, generating and saving to 
                # database if needed
                for i in range (start, start + number):
                    code = ConferenceCode(type=type, number=i)
                
                    code, created = ConferenceCode.objects.get_or_create(type=type, number=i, code=code.code)

                    if request.POST.get('action', None) == "void":
                        
                        code.expired = True
                        code.save()
                        codes.append("voided - " + code.code)
                    else:
                        codes.append(code.code)

                form = CodeGenerationForm()
        
        else:
            form = CodeGenerationForm()
        
        return render_to_response('conference/codes.html',
                                  {'codes': codes,
                                   'form': form,
                                   'conf_codes': CONF_CODES,
                                   'conf_options': CONF_OPTIONS,
                                   'room_choices': ROOM_CHOICES
                                  },
                                  context_instance=RequestContext(request)
                                 )
    else:
        # we've gotten be more standard on whether we render a denied page,
        # or return HttpResponseForbidden - and, eventually, make the UI better
        # in either case.
        return render_to_response('denied.html', context_instance=RequestContext(request))

def lookup_code(request):
    if request.user.has_module_perms('conference'):
        if request.method == 'POST' and request.POST.get('code', None):
            code = get_object_or_none(ConferenceCode, code=request.POST['code'])
            
            if code and code.expired:
                return HttpResponse("voided")
            elif code:
                reg = ConferenceRegistration.objects.filter(code=code, cancelled=False)
                if reg.count():
                    return HttpResponse("used")
                else:
                    return HttpResponse("available")
            else:
                if ConferenceCode.isValid(request.POST['code']):
                    return HttpResponse("not issued")
                else:
                    return HttpResponse("invalid code")
    return HttpResponse("lookup error")
    
