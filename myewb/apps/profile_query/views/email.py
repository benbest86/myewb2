"""myEWB advanced profile query emailer

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

from django.contrib.auth.decorators import permission_required
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, loader, Template
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from profiles.models import MemberProfile
from profile_query.forms.email import EmailForm
from profile_query.views.query import build_profile_query, parse_profile_term

@permission_required('profiles')
def compose(request):
    """
    Display new email form
    """
    if request.method == 'POST':
        form =  EmailForm(request.POST)
    else:
        form = EmailForm()
        
    terms = request.session.get('profilequery', [])
    parsed_terms = []
    for id, term in enumerate(terms):
        # parse to human-readable format
        parsed_terms.append(parse_profile_term(term, id))
        
    return render_to_response("profile_query/email_compose.html",
                              {'form': form,
                               'terms': parsed_terms},
                              context_instance=RequestContext(request))

@permission_required('profiles')
def preview(request):
    """
    Preview email - including HTML body, and ability to edit email
    """
    if request.method == 'POST':
        form = EmailForm(request.POST)
        
        if form.is_valid():
            terms = request.session.get('profilequery', [])
            parsed_terms = []
            for id, term in enumerate(terms):
                # parse to human-readable format
                parsed_terms.append(parse_profile_term(term, id))
                
            recipients = build_profile_query(terms).count()

            return render_to_response("profile_query/email_preview.html",
                                      {'form': form,
                                       'terms': parsed_terms,
                                       'data': form.cleaned_data,
                                       'recipients': recipients},
                                       context_instance=RequestContext(request))
            
        
    else:
        return Http404()
    
@permission_required('profiles')
def send(request):
    """
    Send the email to the current in-cache query, and redirect out
    """
    if request.method == 'POST':
        form = EmailForm(request.POST)
        
        if form.is_valid():     # should always be true..!!!
            
            sender = '"%s" <%s>' % (form.cleaned_data['sendername'],
                                    form.cleaned_data['senderemail'])
    
            terms = request.session.get('profilequery', [])
            recipients = build_profile_query(terms)
            
            emails = []
            for r in recipients:
                emails.append(r.user.email)

            msg = EmailMessage(
                    subject=form.cleaned_data['subject'], 
                    body=form.cleaned_data['body'], 
                    from_email=sender, 
                    to=['mail@my.ewb.ca'],      # one day we'll do individual sending with click tracking
                    bcc=emails,
                    )
            msg.content_subtype = "html"

            msg.send(fail_silently=False)
            
            request.user.message_set.create(message='Email sent')
            return HttpResponseRedirect(reverse('profile_query'))
        
    else:
        return Http404()