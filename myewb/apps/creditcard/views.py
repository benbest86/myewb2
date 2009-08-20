"""myEWB profile views
Functions used to display additional (or replacement) profile-related views not provided by Pinax's profiles app.

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2009-06-22
Last modified: 2009-08-02
@author: Joshua Gorner, Francis Kung, Ben Best
"""

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from creditcard.views import *
from creditcard.forms import *
from creditcard.utils import *

def payment(request):
    form = PaymentForm(request.POST)
    if False: #form.is_valid():
        return HttpResponseRedirect(reverse('profile_detail', kwargs={'username': None }))
        
    else:
        return render_to_response(
                'creditcard/new_payment.html',
                {
                'form': form,
                },
                context_instance=RequestContext(request)
                )
