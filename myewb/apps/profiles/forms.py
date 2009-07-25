"""myEWB profile forms

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on 2009-06-22
Last modified on 2009-07-01
@author Joshua Gorner
"""
from django import forms
from profiles.models import MemberProfile, StudentRecord, WorkRecord

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
		exclude = ('user')
        
class WorkRecordForm(forms.ModelForm):
	"""Add/edit form for the StudentRecord class."""
	class Meta:
		model = WorkRecord
		exclude = ('user')
		
class ProfileSearchForm(forms.Form):
	"""Oneline text box for user search"""
	searchterm = forms.CharField()