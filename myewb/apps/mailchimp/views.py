from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from mailchimp.models import ListEvent, GroupEvent, ProfileEvent 

import settings

def callback(request):
    if request.GET.get('key', None) != settings.MAILCHIMP_CALLBACK_KEY:
        return HttpResponseForbidden('not allowed')
    
    type = request.POST.get('type', None)
    time = request.POST.get('fired_at', None)
    email = request.POST.get('data[email]', None)
    
    if type == 'unsubscribe' or (type == 'cleaned' and request.POST('data[reason]', None) == 'hard'):
        # was there a pending email change in the sync queue? if so, we need 
        # to look up the old email
        e = ProfileEvent.objects.filter(email=email)
        if e.count():
            user = e.user
            
        else:
            # retrieve the user in question
            user = User.objects.get(email=email)
        
        # clear out any pending mailchimp sync requests
        for e in ListEvent.objects.filter(user=user):
            e.delete()
        for e in GroupEvent.objects.filter(user=user):
            e.delete()
        for e in ProfileEvent.objects.filter(user=user):
            e.delete()
            
        # set the nomail flag for this user
        user.nomail = True
        user.save()
    
    return HttpResponse('success')