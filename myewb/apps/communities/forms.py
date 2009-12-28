"""myEWB communities form declarations

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Created on 2009-07-30
@author Joshua Gorner
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from base_groups.models import BaseGroup
from base_groups.forms import BaseGroupForm, GroupMemberForm
from base_groups.helpers import get_valid_parents
from communities.models import Community
from networks.models import Network

class CommunityForm(BaseGroupForm):

    permissions = ( ('P', _("Public group: shows up in listings, and anyone can join")),
                    ('I', _("Invite-only group: shows up in listings, but membership must be approved")),
                    ('R', _("Private group: does not show up in listings, and memberhsip must be approved"))
                  )
                  # could also do "parent only" - "only members of the parent group can see or join this group"?

    group_permissions = forms.ChoiceField(label='Visibility',
                                          choices=permissions,
                                          widget=forms.RadioSelect,
                                          initial='P')
                                          
    # hide these - we'll change the values later depending on the 
    # "group_permissions" field anyway
    invite_only = forms.BooleanField(required=False,
                                     widget=forms.HiddenInput)
    visibility = forms.ChoiceField(required=False,
                                   widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        # get the valid parents for a user if we have a user
        user = kwargs.pop('user', None)
        super(CommunityForm, self).__init__(*args, **kwargs)
        if user:
            group = kwargs.get('instance', None)
            valid_parents = get_valid_parents(user, group=group, model=Network)     # only networks may be parent to a community
            self.fields['parent'].queryset = valid_parents
            
    def clean(self):
        perms = self.cleaned_data['group_permissions']
        
        if perms == 'P':
            self.cleaned_data['visibility'] = 'E'
            self.cleaned_data['invite_only'] = False
        elif perms == 'I':
            self.cleaned_data['visibility'] = 'E'
            self.cleaned_data['invite_only'] = True
        elif perms == 'R':
            self.cleaned_data['visibility'] = 'M'
            self.cleaned_data['invite_only'] = True
        else:
            raise forms.ValidationError(_('Select a valid permissions level'))
            
        return self.cleaned_data
    
    class Meta:
        model = Community
        fields = ('name', 'slug', 'description', 'parent', 'invite_only', 'visibility')

