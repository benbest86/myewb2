"""myEWB profile forms

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on 2009-06-22
Last modified on 2009-12-29
@author Joshua Gorner, Francis Kung, Ben Best
"""
from settings import STATIC_URL
from datetime import date
from django import forms
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from profiles.models import MemberProfile, StudentRecord, WorkRecord
from creditcard.forms import PaymentForm, PaymentFormPreview, ProductWidget
from creditcard.models import Product
from contrib.uni_form.helpers import FormHelper, Submit, Reset
from contrib.uni_form.helpers import Layout, Fieldset, Row, HTML
from siteutils.models import Address, PhoneNumber

class ProfileForm(forms.ModelForm):
	"""Add/edit form for the MemberProfile class."""
	
	gender = forms.ChoiceField(choices=MemberProfile.GENDER_CHOICES,
							   widget=forms.RadioSelect,
							   required=False)
	
	class Meta:
		model = MemberProfile
		fields = ('first_name', 'last_name', 'about', 'gender', 'language', 'date_of_birth')
			
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
		
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ('content_type', 'object_id')

class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = PhoneNumber
        exclude = ('content_type', 'object_id')

MEMBERSHIP_TYPES = (('studues', _("Student ($20)")),
				    ('produes', _("Professional ($40)")))

class MembershipForm(forms.Form):
    membership_type = forms.ChoiceField(choices=MEMBERSHIP_TYPES,
										widget=forms.RadioSelect)
    chapters = [('none', _('(none)'))]
    chapter = forms.ChoiceField(choices=chapters)
    
    helper = FormHelper()
    layout = Layout('membership_type')
    helper.add_layout(layout)
    submit = Submit('submit', 'Continue')
    helper.add_input(submit)
    helper.action = ''
    
    def __init__(self, *args, **kwargs):
        self.base_fields['chapter'].choices = self.chapters     # why do I need to reset this? weird...
        chapterlist = kwargs.pop('chapters', None)
        for chapter in chapterlist:
			self.base_fields['chapter'].choices.append((chapter.slug, chapter.chapter_info.chapter_name))
            
        super(MembershipForm, self).__init__(*args, **kwargs)
    
class MembershipFormPreview(PaymentFormPreview):
    username = None
	
    # this gets called after transaction has been attempted
    def done(self, request, cleaned_data):
    	response = super(MembershipFormPreview, self).done(request, cleaned_data)
    	
    	if response == None:
    		request.user.get_profile().pay_membership()
        	
        	message = loader.get_template("profiles/member_upgraded.html")
        	c = Context({'user': request.user.visible_name()})
        	request.user.message_set.create(message=message.render(c))
        	
        	return HttpResponseRedirect(reverse('profile_detail', kwargs={'username': self.username }))
        else:
        	f = self.form(request.POST)
        	f.trnError = response
        	f.clean
        	context = {'form': f, 'stage_field': self.unused_name('stage'), 'state': self.state}
        	return render_to_response(self.form_template, context, context_instance=RequestContext(request))

class SettingsForm(forms.ModelForm):
    """Edit form for additional MemberProfile settings"""
    
    #show_emails = forms.BooleanField(label="Include emailed posts",
    #                                 required=False)
    #show_replies = forms.BooleanField(label="Include replies",
    #                                  required=False)
    sort_by = forms.ChoiceField(label="Sorting",
                                choices=MemberProfile.SORTING_CHOICES,
                                widget=forms.RadioSelect,
                                required=False)
    replies_as_emails = forms.BooleanField(label="When someone replies to my post",
                                           required=False,
                                           help_text="Send me an email when someone replies to a post that I started")
    replies_as_emails2 = forms.BooleanField(label="When someone replies to my reply",
                                            required=False,
                                            help_text="Send me an email when someone replies to a post that I have also replied to")
    watchlist_as_emails = forms.BooleanField(label="When someone replies to a watchlisted post",
                                             required=False,
                                             help_text="Send me an email when someone replies to a post on my watchlist")
    messages_as_emails = forms.BooleanField(label="When someone sends me a private message",
                                            required=False,
                                            help_text="Send me an email when someone sends me a private message")

    # for custom uni_form layout
    helper = FormHelper()
    layout = Layout(Fieldset('Front page settings',
                             #'show_emails',
                             #'show_replies',
                             'sort_by',
                             css_class='inlineLabels'),
                    Fieldset('Email notices',
                             'replies_as_emails',
                             'replies_as_emails2',
                             'watchlist_as_emails',
                             'messages_as_emails',
                             css_class='inlineLabels'),
                    HTML('<p><input type="submit" value="update"/></p>'))
    helper.add_layout(layout)

    class Meta:
        model = MemberProfile
        fields = (#'show_emails',
                  #'show_replies',
                  'sort_by',
                  'replies_as_emails',
                  'replies_as_emails2',
                  'watchlist_as_emails',
                  'messages_as_emails')
