"""myEWB base groups form declarations

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Last modified on 2009-07-29
@author Joshua Gorner
"""
from django import forms
from django.utils.translation import ugettext_lazy as _

from base_groups.models import BaseGroup, GroupMember, GroupLocation

class BaseGroupForm(forms.ModelForm):
    
    slug = forms.SlugField(max_length=20,
        help_text = _("a short version of the name consisting only of letters, numbers, underscores and hyphens."),
        error_message = _("This value must contain only letters, numbers, underscores and hyphens."))
            
    def clean_slug(self):
        
        if BaseGroup.objects.filter(slug__iexact=self.cleaned_data["slug"]).count() > 0:
            if self.instance and self.cleaned_data["slug"] == self.instance.slug:
                pass # same instance
            else:
                raise forms.ValidationError(_("A group (network, community or project) already exists with that slug."))
        return self.cleaned_data["slug"].lower()
    
    def clean_name(self):

        if BaseGroup.objects.filter(name__iexact=self.cleaned_data["name"]).count() > 0:
            if self.instance and self.cleaned_data["name"] == self.instance.name:
                pass # same instance
            else:
                raise forms.ValidationError(_("A group (network, community or project) already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        abstract = True

class GroupMemberForm(forms.ModelForm):
    # we may need something else in here at some point...
    class Meta:
        abstract = True
        
class GroupLocationForm(forms.ModelForm):
    
    class Meta:
        model = GroupLocation
        fields = ('place', 'latitude', 'longitude')
