"""myEWB advanced profile query emailer

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""
from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse

class EmailForm(forms.Form):
    subject = forms.CharField(max_length=250)
    body = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))
    sendername = forms.CharField(max_length=75)
    senderemail = forms.EmailField()
