"""myEWB base groups form declarations

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Last modified on 2009-07-29
@author Joshua Gorner
"""
from settings import STATIC_URL
from django import forms
#from django.utils.translation import ugettext_lazy as _
from siteutils.countries import _

from base_groups.models import BaseGroup, GroupMember, GroupLocation, InvitationToJoinGroup
from base_groups.helpers import get_valid_parents
from user_search.forms import MultipleUserField

class BaseGroupForm(forms.ModelForm):
    
    slug = forms.SlugField(max_length=20,
        label = _("Short name"),
        help_text = _("a short version of the name consisting only of letters, numbers, underscores and hyphens."),
        error_message = _("This value must contain only letters, numbers, underscores and hyphens."))
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)     # pop off user arg, in case subclass doesn't use it
        super(BaseGroupForm, self).__init__(*args, **kwargs)
            
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
    
    def clean_welcome_email(self):
        self.cleaned_data['welcome_email'] = self.cleaned_data['welcome_email'].strip()
        return self.cleaned_data['welcome_email']
    
    class Meta:
        abstract = True

class GroupInviteForm(forms.ModelForm):
    user = MultipleUserField(label=_("User"))
    
    class Meta:
        model = InvitationToJoinGroup
        fields = ('user', 'message')
        
class GroupMemberForm(forms.ModelForm):
    user = MultipleUserField(label=_("User"))

    class Meta:
        model = GroupMember        
        fields = ('user', 'is_admin', 'admin_title')
        
    class Media:
        js = (STATIC_URL + 'js/base_groups/member.js',)

class EditGroupMemberForm(forms.ModelForm):
    
    class Meta:
        model = GroupMember        
        fields = ('is_admin', 'admin_title')
        
    class Media:
        js = (STATIC_URL + 'js/base_groups/member.js',)

class GroupLocationForm(forms.ModelForm):
    
    class Meta:
        model = GroupLocation
        fields = ('place', 'latitude', 'longitude')

class GroupAddEmailForm(forms.Form):
    email = forms.EmailField(label='', required=True,
                             initial='(your email address)')