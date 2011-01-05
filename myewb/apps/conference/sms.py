"""myEWB conference SMS noties

This file is part of myEWB
Copyright 2009-2010 Engineers Without Borders Canada

@author: Francis Kung
"""

import settings
from datetime import date, datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string

from threading import Thread
from twilio import twilio
from mailer import send_mail

from conference.forms import ConferenceSmsForm, SMS_CHOICES
from conference.models import ConferenceRegistration, ConferenceSession, ConferenceCellNumber, ConferencePhoneFrom
from siteutils.shortcuts import get_object_or_none

CONFERENCE_DAYS = (('thurs', 'Thursday', 13),
                   ('fri', 'Friday', 14),
                   ('sat', 'Saturday', 15))

def do_send_sms(args):
    try:
        api = settings.TWILIO_API_VERSION
        sid = settings.TWILIO_ACCOUNT_SID
        token = settings.TWILIO_ACCOUNT_TOKEN

        account = twilio.Account(sid, token)
        
        for x in args:
            response = account.request('/%s/Accounts/%s/SMS/Messages' % (api, sid),
                                       'POST', x)
    except Exception, e:
        response = e.read()

        send_mail(subject="sms error",
                  txtMessage=response,
                  htmlMessage=None,
                  fromemail="itsupport@ewb.ca",
                  recipients=['franciskung@ewb.ca',],
                  use_template=False)
    

@login_required
def send_sms(request, session=None):
    if not request.user.has_module_perms("conference"):
        return HttpResponseRedirect(reverse('conference_schedule'))
    
    s = get_object_or_none(ConferenceSession, id=session)
    response = None

    if request.method == 'POST':
        api = settings.TWILIO_API_VERSION
        sid = settings.TWILIO_ACCOUNT_SID
        token = settings.TWILIO_ACCOUNT_TOKEN
        
        form = ConferenceSmsForm(request.POST)
        
        if s:
            del(form.fields['grouping'])

        if form.is_valid():
            success = 0
            failed = 0
            
            registrations = []
            if s:
                registrations = ConferenceRegistration.objects.filter(user__in=list(s.attendees.all()))
            elif form.cleaned_data['grouping'] == 'all':
                registrations = ConferenceRegistration.objects.all()
            elif form.cleaned_data['grouping'] == 'internal':
                registrations = ConferenceRegistration.objects.filter(~Q(type__contains='day'))
            elif form.cleaned_data['grouping'] == 'external':
                registrations = ConferenceRegistration.objects.filter(type__contains='day')
            elif form.cleaned_data['grouping'] == 'alumni':
                registrations = ConferenceRegistration.objects.filter(type__contains='alumni')
            elif form.cleaned_data['grouping'] == 'hotel':
                registrations = ConferenceRegistration.objects.filter(Q(type__contains='single') | Q(type__contains='double'))
            elif form.cleaned_data['grouping'] == 'nohotel':
                registrations = ConferenceRegistration.objects.filter(Q(type__contains='nohotel') | Q(type__contains='alumni'))
            elif form.cleaned_data['grouping'] == 'nohotel-all':
                registrations = ConferenceRegistration.objects.filter(~Q(type__contains='single'), ~Q(type__contains='double'))
            
            registrations = registrations.filter(cancelled=False, cellphone__isnull=False, cellphone_optout__isnull=True)
            
            if not s and form.cleaned_data['grouping'] == 'all':
                registrations = list(registrations)
                registrations.extend(list(ConferenceCellNumber.objects.filter(cellphone_optout__isnull=True)))
            
            # Twilio
            account = twilio.Account(sid, token)
            thread_list = {}
            for r in registrations:
                if r.cellphone_optout or not r.cellphone:
                    continue
                
                fromnumber = r.cellphone_from
                if not fromnumber:
                    numbers = ConferencePhoneFrom.objects.order_by('accounts')
                    fromnumber = numbers[0]
                    r.cellphone_from=fromnumber
                    r.save()
                    fromnumber.accounts = fromnumber.accounts + 1
                    fromnumber.save() 
                        
                d = {'From': fromnumber.number,   #  '415-599-2671',
                     'To': r.cellphone,
                     'Body': form.cleaned_data['message']}
                
                if fromnumber.number not in thread_list:
                    thread_list[fromnumber.number] = []
                thread_list[fromnumber.number].append(d)
                
            try:
                for i in thread_list:
                    t = Thread(target=do_send_sms, args=(thread_list[i],))
                    t.start()
                
            except Exception, e:
                #response = e.read()
                failed = failed + 1
            else:
                success = success + 1

            response = ""
            if failed:
                response = "%s<br/>Messages queued for sending, but some errors encountered =(" % response
            else:
                response = "%s<br/>Messages queued for sending!" % response
            
            """
            # ThunderTexting, simple GET
            import urllib
            try:
                params = {}
                params['CellNumber'] = '000-000-0000'
                params['MessageBody'] = form.cleaned_data['message']
                params['AccountKey'] = 'PPD843rw14'
                
                encoded = urllib.urlencode(params)
                handle = urllib.urlopen("http://thundertexting.com/sendsms.aspx?%s" % encoded)
                response = handle.read()
                #response = "http://thundertexting.com/sendsms.aspx?%s" % encoded
                
            except Exception, e:
                response = r.read()
            """

            """
            # ThunderTexting, SOAP
            from suds.client import Client
            try:
                url = 'http://thundertexting.com/SendSMS.asmx?WSDL'
                client = Client(url)
                
                response = client.service.SendMessageWithReference(CellNumber='000-000-0000',
                                                                   MessageBody=form.cleaned_data['message'],
                                                                   AccountKey=settings.THUNDERTEXTING_KEY,
                                                                   Reference='test1')
            except Exception, e:
                response = r.read()
            """
            
            """
            # ThunderTexting, SOAP batch send
            try:
                from suds.client import Client
                url = 'http://thundertexting.com/SendSMS.asmx?WSDL'
                client = Client(url)

                numbers = []
                for r in registrations:
                    if r.cellphone and not r.cellphone_optout:
                        numbers.append(r.cellphone)
                
                # cell number should already be normalized to 123-456-7890
                response = client.service.SendBulkMessage(CellNumbers=numbers,
                                                          MessageBody=form.cleaned_data['message'],
                                                          AccountKey=settings.THUNDERTEXTING_KEY,
                                                          Reference=datetime.now())
            except Exception, e:
                response = r.read()
            """
            
            """
            for r in registrations:
                if hasattr(r, 'user'):
                    if r.cellphone and not r.cellphone_optout:
                        response = "%s<br/>%s %s - %s\n" % (response, r.user.first_name, r.user.last_name, r.type)
                else:
                    response = "%s<br/>%s\n" % (response, r.cellphone)
                    
            if not response:
                response = "No recipients matched your query."
            """
                
    else:
        form = ConferenceSmsForm()
        if s:
            del(form.fields['grouping'])
            
    context = {}
    if s:
        context['session'] = s
    if response:
        context['response'] = response
    else:
        context['form'] = form
        
    return render_to_response("conference/schedule/sms.html",
                              context,
                              context_instance = RequestContext(request))

# This requires mailbox support; see sms_poll.php and put it on a cron =)
def stop_sms(request):
    """
    ThunderTexting format:
    
    Date Received: 1/4/2011 8:48:41 PM
    From Phone Number: 1416xxxxxxx
    Their Message: You tell me!
    
    Newline test
    --------------------------
    This is most likely a response to the following message you sent -  
    Date Sent: 1/4/2011 8:48:03 PM
    To Phone Number: 416xxxxxxx
    Your Message: ok, now what's next...!
    Your Reference: test1
    
    if request.method != 'POST' or not request.POST.get('message', None):
        return HttpResponse("not supported")

    result = ""
    
    message = request.POST.get('message', None)
    lines = message.split("\n")
    date = lines[0]
    fromnumber = lines[1]
    
    tempa, tempb, fromnumber = fromnumber.partition(':')
    fromnumber = fromnumber.strip()
    
    if fromnumber[0:1] == '1':
        fromnumber = fromnumber[1:]
    
    txtmessage = lines[2]
    for i in range(3, len(lines)):
        if lines[i].startswith('----'):
            break
        txtmessage = txtmessage + "\n" + lines[i]
    """
    
    """
    Twilio format.  So much easier.
    """
    if request.method != 'POST' or not request.POST.get('From', None) or not request.POST.get('Body', None):
        return HttpResponse("not supported")

    tonumber = request.POST.get('To', None)
    fromnumber = request.POST.get('From', None)
    txtmessage = request.POST.get('Body', None)
    result = ""
    
    if fromnumber[0:1] == '1':
        fromnumber = fromnumber[1:]
    elif fromnumber[0:2] == '+1':
        fromnumber = fromnumber[2:]
        
    if tonumber[0:1] == '1':
        tonumber = tonumber[1:]
    elif tonumber[0:2] == '+1':
        tonumber = tonumber[2:]

    if fromnumber == '5193627821' or tonumber == '5193627821':
        return HttpResponse("")
        
    txtmessage = txtmessage.strip().lower()
    
    if txtmessage.find('stop') != -1:
        result = result + "stopping\n"
        r = ConferenceRegistration.objects.filter(cellphone=fromnumber, cancelled=False)
        
        if fromnumber and r.count():
            for reg in r:
                result = result + "goodbye %s\n" % reg.user.email
                reg.cellphone_optout = datetime.now()
                reg.save()
                provider = reg.cellphone_from
                if provider:
                    provider.accounts = provider.accounts - 1
                    provider.save()
                
        numbers = ConferenceCellNumber.objects.filter(cellphone=fromnumber, cellphone_optout__isnull=True)
        if fromnumber and numbers.count():
            for n in numbers:
                n.cellphone_optout = datetime.now()
                n.save()
                provider = n.cellphone_from
                if provider:
                    provider.accounts = provider.accounts - 1
                    provider.save()
                    
        xmlresponse = """<?xml version="1.0" encoding="UTF-8" ?>
<Response>
    <Sms>You have been unsubscribed.  To re-subscribe to EWB National Conference 2011 notices, reply with START</Sms>
</Response>
"""
        return HttpResponse(xmlresponse)
            
                
    elif txtmessage.find('start') != -1:
    #else:
        r = ConferenceRegistration.objects.filter(cellphone=fromnumber, cancelled=False)
        numbers = ConferenceCellNumber.objects.filter(cellphone=fromnumber)

        if r.count():
            reg = r[0]
            reg.cellphone_optout = None
            reg.save()
            
            if reg.cellphone_from:
                provider = reg.cellphone_from
            else:
                provider, created = ConferencePhoneFrom.objects.get_or_create(number=tonumber)
                reg.cellphone_from = provider
                reg.save()
            provider.accounts = provider.accounts + 1
            provider.save()
        
        elif numbers.count():
            result = result + "already found %s\n" % fromnumber
            n = numbers[0]
            n.cellphone_optout = None
            n.save()
            
            if n.cellphone_from:
                provider = n.cellphone_from
            else:
                provider, created = ConferencePhoneFrom.objects.get_or_create(number=tonumber)
                n.cellphone_from = provider
                n.save()
            provider.accounts = provider.accounts + 1
            provider.save()
                
        else:
            provider, created = ConferencePhoneFrom.objects.get_or_create(number=tonumber)
            ConferenceCellNumber.objects.create(cellphone=fromnumber, cellphone_from=provider)
            result = result + "adding %s\n" % fromnumber
    
        xmlresponse = """<?xml version="1.0" encoding="UTF-8" ?>
<Response>
    <Sms>Welcome to the EWB National Conference 2011 notices list.  To unsubscribe, reply with STOP</Sms>
</Response>
"""
        return HttpResponse(xmlresponse)
    
    #else:
    #    result = result + "dunno what to do\n"
    #    result = result + txtmessage
    else:
        return HttpResponse("")

        
    return HttpResponse(result)
