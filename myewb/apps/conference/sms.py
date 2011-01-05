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

from conference.forms import ConferenceSmsForm, SMS_CHOICES
from conference.models import ConferenceRegistration, ConferenceSession, ConferenceCellNumber
from siteutils.shortcuts import get_object_or_none

CONFERENCE_DAYS = (('thurs', 'Thursday', 13),
                   ('fri', 'Friday', 14),
                   ('sat', 'Saturday', 15))

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
                registrations.extend(list(ConferenceCellNumber.objects.filter(opt_out__isnull=True)))
            
            
            """
            # Twilio, requiring us to disperse over a number of phone numbers...
            
            for r in registrations:
                if r.cellphone_optout or not r.cellphone:
                    continue
                
                fromnumber = r.cellphone_from
                if not fromnumber:
                    numbers = ConferencePhoneFrom.objects.filter(accounts__lt=10)
                    if numbers.count():
                        fromnumber = numbers[0]
                        r.cellphone_from=fromnumber
                        r.save()
                    else:
                        # create new number via api
                        pass
                        
                d = {'From': fromnumber.number,   #  '415-599-2671',
                     'To': r.cellphone,
                     'Body': form.cleaned_data['message']}
                try:
                    from twilio import twilio
                    account = twilio.Account(sid, token)
                    response = account.request('/%s/Accounts/%s/SMS/Messages' % (api, sid),
                                               'POST', d)
                    
                except Exception, e:
                    #response = e.read()
                    failed = failed + 1
                else:
                    success = success + 1
            """
            
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
            
            for r in registrations:
                if hasattr(r, 'user'):
                    if r.cellphone and not r.cellphone_optout:
                        response = "%s<br/>%s %s - %s\n" % (response, r.user.first_name, r.user.last_name, r.type)
                elif hasattr(r, 'number'):
                    response = "%s<br/>%s\n" % (response, r.number)
                else:
                    response = "%s<br/>unknown\n"
                    
            if not response:
                response = "No recipients matched your query."
                
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
    if request.method != 'POST' or not request.POST.get('message', None):
        return HttpResponse("not supported")

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
    """
    
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
    
    txtmessage = txtmessage.strip().lower()
    if txtmessage.find('stop') != -1:
        result = result + "stopping\n"
        r = ConferenceRegistration.objects.filter(cellphone=fromnumber, cancelled=False)
        
        if fromnumber and r.count():
            for reg in r:
                result = result + "goodbye %s\n" % reg.user.email
                reg.cellphone_optout = datetime.now()
                reg.save()
                
        numbers = ConferenceCellNumber.objects.filter(number=fromnumber, opt_out__isnull=True)
        if fromnumber and numbers.count():
            for n in numbers:
                n.opt_out = datetime.now()
                n.save()
            
                
    #elif txtmessage.find('start') != -1:
    else:
        numbers = ConferenceCellNumber.objects.filter(number=fromnumber, opt_out__isnull=True)
        if not numbers.count():
            ConferenceCellNumber.objects.create(number=fromnumber)
            result = result + "adding %s\n" % fromnumber
        else:
            result = result + "already found %s\n" % fromnumber
    
    #else:
    #    result = result + "dunno what to do\n"
    #    result = result + txtmessage

        
    return HttpResponse(result)
