"""myEWB advanced profile query exporter

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse

class CsvForm(forms.Form):
    first_name = forms.BooleanField(label='First Name', required=False)
    last_name = forms.BooleanField(label='Last Name', required=False)
    email = forms.BooleanField(label='Email', required=False)
    gender = forms.BooleanField(label='Gender', required=False)
    language = forms.BooleanField(label='Language', required=False)
    date_of_birth = forms.BooleanField(label='Date of Birth', required=False)
