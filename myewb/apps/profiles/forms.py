"""myEWB profile forms

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on 2009-06-22
Last modified on 2009-07-31
@author Joshua Gorner, Francis Kung, Ben Best
"""
from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext_lazy as _
from profiles.models import MemberProfile, StudentRecord, WorkRecord
from creditcard.forms import PaymentForm, PaymentFormPreview, ProductWidget
from creditcard.models import Product
from uni_form.helpers import FormHelper, Submit, Reset
from uni_form.helpers import Layout, Fieldset, Row, HTML

class ProfileForm(forms.ModelForm):
	"""Add/edit form for the MemberProfile class."""
	
	class Meta:
		model = MemberProfile
		exclude = ('name', 'location', 'user', 'blogrss', 'timezone', 'language',
			'twitter_user', 'twitter_password', 'current_login', 'last_login', 'login_count',
			'address_updated', 'membership_expiry', 'contact_info')
			
class StudentRecordForm(forms.ModelForm):
	"""Add/edit form for the StudentRecord class."""
	class Meta:
		model = StudentRecord
		exclude = ('user', 'network')
        
class WorkRecordForm(forms.ModelForm):
	"""Add/edit form for the StudentRecord class."""
	class Meta:
		model = WorkRecord
		exclude = ('user', 'network')

MEMBERSHIP_TYPES = (('studues', _("Student ($20)")),
				    ('produes', _("Professional ($40)")))

class MembershipForm(forms.Form):
	membership_type = forms.ChoiceField(choices=MEMBERSHIP_TYPES,
										widget=forms.RadioSelect)
	
	#TODO
	#chapter = forms.ForeignKey blah blah
	
	helper = FormHelper()
	layout = Layout('membership_type')
	helper.add_layout(layout)
	submit = Submit('submit', 'Continue')
	helper.add_input(submit)
	helper.action = ''
    
class MembershipFormPreview(PaymentFormPreview):
    username = None
	
    def parse_params(self, *args, **kwargs):
        self.username = kwargs['username']
        
    # this gets called after transaction has been attempted
    def done(self, request, cleaned_data):
        response = super(MembershipFormPreview, self).done(request, cleaned_data)
        
        if response == None:
            message = loader.get_template("profiles/member_upgraded.html")
            c = Context({'user': self.username})
            request.user.message_set.create(message=message.render(c))

            return HttpResponseRedirect(reverse('profile_detail', kwargs={'username': self.username }))
        else:
        	f = self.form(request.POST)
        	f.trnError = response
        	f.clean
        	context = {'form': f, 'stage_field': self.unused_name('stage'), 'state': self.state}
        	return render_to_response(self.form_template, context, context_instance=RequestContext(request))
