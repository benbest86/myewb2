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

from base_groups.models import BaseGroup

from profile_query.types import *
from profile_query.models import Query

class ProfileInfoQueryWidget(forms.MultiWidget):
    """
    Widget to display advanced profile-based query fields
    """
    def __init__(self, *args, **kwargs):
        
        widgets = (forms.Select(choices=PROFILE_CHOICES.items()),
                   forms.Select(choices=STRING_COMPARISONS.items()),
                   forms.TextInput())
        
        super(ProfileInfoQueryWidget, self).__init__(widgets, *args, **kwargs)
        
    def decompress(self, value):
        if value:
            return value.split("|")[1:]
        else:
            return [None, None, None]

    def format_output(self, rendered_widgets):
        widgetContext = {'attribute': rendered_widgets[0],
                         'comparison': rendered_widgets[1],
                         'queryvalue': rendered_widgets[2]}
        return render_to_string("profile_query/widget_profileinfo.html",
                                widgetContext)
    
class ProfileInfoQueryField(forms.MultiValueField):
    """
    Field for advanced query-based fields
    """
    widget = ProfileInfoQueryWidget
    
    def __init__(self, *args, **kwargs):
        fields = (forms.ChoiceField(choices=PROFILE_CHOICES.items()),
                  forms.ChoiceField(choices=STRING_COMPARISONS.items()),
                  forms.CharField(max_length=250))
        
        super(ProfileInfoQueryField, self).__init__(fields, *args, **kwargs)
        
    def compress(self, data_list):
        return "profile|" + "|".join(data_list)
        
class ProfileQueryForm(forms.Form):
    queryfields = ProfileInfoQueryField(label="")

## --- now the same thing, but for group memberships --- ## 

class GroupMembershipQueryWidget(forms.MultiWidget):
    """
    Widget to display advanced profile-based query fields
    """
    def __init__(self, *args, **kwargs):
        groups = {}
        for g in BaseGroup.objects.filter(is_active=True):
            groups[g.slug] = g.name
        
        """
        widgets = (forms.Select(choices=GROUP_CHOICES.items()),
                   forms.Select(choices=groups.items()),
                   forms.Select(choices=DATE_COMPARISONS.items()),
                   forms.TextInput())
        """
        widgets = (forms.Select(choices=GROUP_CHOICES2.items()),
                   forms.Select(choices=groups.items()))
        
        super(GroupMembershipQueryWidget, self).__init__(widgets, *args, **kwargs)
        
    def decompress(self, value):
        if value:
            return value.split("|")[1:]
        else:
            return [None, None, None]

    def format_output(self, rendered_widgets):
        """
        widgetContext = {'operation': rendered_widgets[0],
                         'group': rendered_widgets[1],
                         'comparison': rendered_widgets[2],
                         'date': rendered_widgets[3]}
        """
        widgetContext = {'operation': rendered_widgets[0],
                         'group': rendered_widgets[1]}
        return render_to_string("profile_query/widget_groupmembership.html",
                                widgetContext)
    
class GroupMembershipQueryField(forms.MultiValueField):
    """
    Field for advanced query-based fields
    """
    widget = GroupMembershipQueryWidget
    
    def __init__(self, *args, **kwargs):
        """
        fields = (forms.ChoiceField(choices=GROUP_CHOICES.items()),
                  forms.SlugField(),
                  forms.ChoiceField(choices=DATE_COMPARISONS.items()),
                  forms.DateField())
        """
        fields = (forms.ChoiceField(choices=GROUP_CHOICES2.items()),
                  forms.SlugField())
        
        super(GroupMembershipQueryField, self).__init__(fields, *args, **kwargs)
        
    def compress(self, data_list):
        return "group|" + "|".join(data_list)

class GroupQueryForm(forms.Form):
    queryfields = GroupMembershipQueryField(label="")

# --- other misc forms --- #
class QueryNameForm(forms.ModelForm):
    """
    Allows users to save a query for later use
    """
    class Meta:
        model = Query
        fields = ('name', 'shared')
