"""myEWB network form declarations

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Last modified on 2009-07-29
@author Joshua Gorner
"""

from django import forms
from django.forms import widgets
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.forms.fields import email_re
from django.contrib.localflavor.ca import forms as caforms

from base_groups.models import BaseGroup
from base_groups.forms import BaseGroupForm
from networks.models import Network, ChapterInfo, EmailForward
        
class NetworkForm(BaseGroupForm):

    class Meta:
        model = Network
        fields = ('name', 'slug', 'network_type', 'description')

class NetworkBulkImportForm(forms.Form):
    emails = forms.CharField(widget = forms.Textarea)

    def clean_emails(self):
        data = self.cleaned_data['emails']
        bad_emails = []
        for email in data.split():
            if not email_re.match(email):
                bad_emails.append(email)
        if bad_emails:
            raise forms.ValidationError('\n'.join(['%s is not a valid email.' % bad_email for bad_email in bad_emails]))
        return data

    
class NetworkUnsubscribeForm(forms.Form):
    email = forms.CharField()
        
class ChapterInfoForm(forms.ModelForm):
    province = caforms.CAProvinceField(widget=caforms.CAProvinceSelect())
    postal_code = caforms.CAPostalCodeField()
    phone = caforms.CAPhoneNumberField()
    fax = caforms.CAPhoneNumberField(required=False)
    
    class Meta:
        model = ChapterInfo
        fields = ('chapter_name', 'network', 'street_address', 'street_address_two', 'city', 'province', 'postal_code', 'phone', 'fax')

class PartialEmailField(forms.EmailField):
    def clean(self, value):
        # call super, but tack on the domain
        super(PartialEmailField, self).clean("%s%s" % (value, "@ewb.ca"))
        
        # if super.clean failed, it will have thrown a ValidationError
        # so we can assume we have a good partial here
        return value

class PartialEmailWidget(forms.TextInput):
    def render(self, name, value, attrs=None):
        html = super(PartialEmailWidget, self).render(name, value, attrs)
        
        html = "%s %s" % (html, "@<em>chaptername</em>.ewb.ca")
        return mark_safe(html)
        
class EmailForwardForm(forms.ModelForm):
    address = PartialEmailField(widget=PartialEmailWidget)
    
    def __init__(self, *args, **kwargs):
        network = kwargs.pop('network', None)
        super(EmailForwardForm, self).__init__(*args, **kwargs)
        self.network = network
            
    def clean_address(self):
        partial = self.cleaned_data.get('address', '')
        address = "%s@%s.ewb.ca" % (partial, self.network.slug)
        
        return address

    def clean_user(self):
        data = self.cleaned_data
        user = data['user']
        if not user.email:
            raise forms.ValidationError("Cannot create forward - user does not have an email set.")
        return user
    
    class Meta:
        model = EmailForward
        fields = ('user', 'address')
        # TODO: the user field should be a search, not a dropdown
        