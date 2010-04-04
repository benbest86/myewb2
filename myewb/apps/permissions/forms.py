"""myEWB permission form declarations

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from user_search.forms import MultipleUserField

class AddPermissionForm(forms.Form):
    user = MultipleUserField(label=_(u"User"))
