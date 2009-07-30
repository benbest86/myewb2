"""myEWB base groups form declarations

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Last modified on 2009-07-29
@author Joshua Gorner
"""
from django import forms
from django.utils.translation import ugettext_lazy as _

from base_groups.models import BaseGroup, GroupMember, GroupLocation

class GroupMemberForm(forms.ModelForm):

    class Meta:
        model = GroupMember
        fields = ('user', 'is_admin', 'admin_title')
        
class GroupLocationForm(forms.ModelForm):
    
    class Meta:
        model = GroupLocation
        fields = ('place', 'latitude', 'longitude')
