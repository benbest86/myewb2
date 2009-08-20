"""myEWB network form declarations

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Last modified on 2009-07-29
@author Joshua Gorner
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from base_groups.models import BaseGroup
from base_groups.forms import BaseGroupForm
from networks.models import Network
        
class NetworkForm(BaseGroupForm):

    class Meta:
        model = Network
        fields = ('name', 'slug', 'network_type', 'description', 'private')