"""myEWB advanced profile query forms

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
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from profile_query.types import *

class ProfileInfoQueryWidget(forms.MultiWidget):
    """
    Widget to display advanced profile-based query fields
    """
    def __init__(self, *args, **kwargs):
        
        widgets = (forms.Select(choices=FIELD2.items()),
                   forms.Select(choices=FIELD3.items()),
                   forms.TextInput())
        
        super(ProfileInfoQueryWidget, self).__init__(widgets, *args, **kwargs)
        
    def decompress(self, value):
        if value:
            return value.split("|")
        else:
            return [None, None, None]

    def format_output(self, rendered_widgets):
        widgetContext = {'attribute': rendered_widgets[0],
                         'comparison': rendered_widgets[1],
                         'queryvalue': rendered_widgets[2]}
        return render_to_string("profile_query/widget_profileinfo.html",
                                widgetContext)
    
class ProfileInfoQueryField(forms.MultiValueField):
    widget = ProfileInfoQueryWidget
    
    def __init__(self, *args, **kwargs):
        fields = (forms.ChoiceField(choices=FIELD2.items()),
                  forms.ChoiceField(choices=FIELD3.items()),
                  forms.CharField(max_length=250))
        
        super(ProfileInfoQueryField, self).__init__(fields, *args, **kwargs)
        
    def compress(self, data_list):
        return "|".join(data_list)
        
class ProfileQueryForm(forms.Form):
    queryfields = ProfileInfoQueryField(label="")
