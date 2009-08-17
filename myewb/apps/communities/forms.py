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
from communities.models import Community, CommunityMember

class CommunityForm(BaseGroupForm):
    class Meta:
        model = Community
        fields = ('name', 'slug', 'description', 'parent', 'private', 'visibility')
        
class CommunityMemberForm(GroupMemberForm):

    class Meta:
        model = CommunityMember
        fields = ('user', 'is_admin', 'admin_title')