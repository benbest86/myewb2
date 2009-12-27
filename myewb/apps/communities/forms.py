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
    def __init__(self, *args, **kwargs):
        # get the valid parents for a user if we have a user
        user = kwargs.pop('user', None)
        super(CommunityForm, self).__init__(*args, **kwargs)
        if user:
            group = kwargs.get('instance', None)
            valid_parents = get_valid_parents(user, group=group, model=Network)     # only networks may be parent to a community
            self.fields['parent'].queryset = valid_parents
    
    class Meta:
        model = Community
        fields = ('name', 'slug', 'description', 'parent', 'invite_only', 'visibility')
