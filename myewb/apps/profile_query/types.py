"""myEWB advanced profile query

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""
from settings import STATIC_URL
from django import forms
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

DATECHOICES = {'current': 'Current',
              'on': 'On',
              'since': 'Since',
              'until': 'Until'}

STRINGCHOICES = {'exact': 'equals (exact)',
                'iexact': 'equals (case-insensitive)',
                'contains': 'contains',
                'icontains': 'contains (case-insensitive)',
                'istartswith': 'starts with',
                'iendswith': 'ends with',
                'isnull': 'is blank'}

PROFILECHOICES = {'first_name': 'First Name',
                  'last_name': 'Last Name',
                  'user__emailaddress__email': 'Email',
                  'gender': 'Gender (M or F)',
                  'language': 'Language (E or F)',
                  'date_of_birth': 'Date of birth',             # FIXME: need date selector
                  'membership_expiry': 'Membership expiry',     # FIXME: need date selector
                  'previous_login': 'Last sign-in',             # FIXME: need date selector
                  'login_count': 'Number of sign-ins',
                  'addresses__city': 'City',
                  'addresses__province': 'Province',
                  'addresses__country': 'Country'}

PROFILEVALIDATION = {'name': STRINGCHOICES,
                     'city': STRINGCHOICES,
                     'email': STRINGCHOICES}

FIELD1 = {'profile': 'Profile',
         'groups': 'Group membership'}

FIELD2 = PROFILECHOICES

FIELD3 = STRINGCHOICES
