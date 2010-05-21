"""myEWB 

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, loader, Template
from django.utils.translation import ugettext_lazy as _
from mailer import send_mail

def feedback(request):
    if request.method == 'POST':
        username = request.POST.get('feedback-username', None)
        visiblename = request.POST.get('feedback-visiblename', None)
        systememail = request.POST.get('feedback-email-h', None)
        email = request.POST.get('feedback-email', None)
        text = request.POST.get('feedback-text', None)
        category = request.POST.get('feedback-category', None)

        body = """myEWB 1.5 feedback received!

Category: %s

From: %s

Feeback:
%s
""" % (category, email, text)

        send_mail(subject="myEWB feedback",
                  txtMessage=body,
                  htmlMessage=None,
                  fromemail="myEWB notices <system@my.ewb.ca>",
                  recipients=["feedback@my.ewb.ca"],
                  use_template=False)
    return HttpResponse("thanks")
