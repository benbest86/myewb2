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
                    ('R', _("Private group: does not show up in listings, and membership must be approved"))
                  )
                  # could also do "parent only" - "only members of the parent group can see or join this group"?

    #parent = forms.ChoiceField(label='Chapter',
    #                           help_text="If a chapter set, this community will show up on the chapter's info page and chapter execs will also have access to it.")

    group_permissions = forms.ChoiceField(label='Visibility',
                                          choices=permissions,
                                          widget=forms.RadioSelect,
                                          initial='P')
                                          
    # hide these - we'll change the values later depending on the 
    # "group_permissions" field anyway
    invite_only = forms.BooleanField(required=False,
                                     widget=forms.HiddenInput)
    visibility = forms.ChoiceField(required=False,
                                   widget=forms.HiddenInput,
                                   choices=BaseGroup.VISIBILITY_CHOICES)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CommunityForm, self).__init__(*args, **kwargs)

        # get the valid parents for a user if we have a user
        if user:
            group = kwargs.get('instance', None)
            valid_parents = get_valid_parents(user, group=group, model=Network)     # only networks may be parent to a community
            self.fields['parent'].queryset = valid_parents
            self.fields['parent'].label = "Chapter"
            self.fields['parent'].help_text = "If a chapter set, this community will show up on the chapter's info page and chapter execs will also have access to it."
            
        # set the initial visibility state (since it's not a direct mapping to 
        # a model field, it isn't done automatically)        
        if self.instance.pk:
            # not sure why "if self.instance" doesn't work; that's set even for a new form

            if not self.instance.invite_only:
                self.fields['group_permissions'].initial='P'
            elif self.instance.visibility == 'E':
                self.fields['group_permissions'].initial='I'
            elif self.instance.visibility == 'M':
                self.fields['group_permissions'].initial='R'

            # hack way to see if this is actually a NationalRepList or ExecList instance
            # (self.instance.__class__ doesn't work, since the object is instantiated as a community)
            try:
                if getattr(self.instance, "nationalreplist"):
                    del self.fields['group_permissions']
            except: 
                pass
            try:
                if getattr(self.instance, "execlist"):
                    del self.fields['group_permissions']
            except:
                pass
            
    def clean(self):
        perms = self.cleaned_data.get('group_permissions', None)
        
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
            # don't change anything
            pass
            
        return super(CommunityForm, self).clean()
    
    class Meta:
        model = Community
        fields = ('name', 'slug', 'description', 'parent', 'invite_only', 'visibility',
                  'welcome_email')

