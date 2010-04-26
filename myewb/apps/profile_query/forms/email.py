"""myEWB advanced profile query emailer

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""
from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from lxml.html.clean import clean_html, autolink_html

class EmailForm(forms.Form):
    subject = forms.CharField(max_length=250)
    body = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))
    sendername = forms.CharField(max_length=75)
    senderemail = forms.EmailField()

    def clean_body(self):
        body = self.cleaned_data.get('body', '')

        # validate HTML content
        # Additional options at http://codespeak.net/lxml/lxmlhtml.html#cleaning-up-html
        body = clean_html(body)
        #body = autolink_html(body)
    
        self.cleaned_data['body'] = body
        return self.cleaned_data['body']
