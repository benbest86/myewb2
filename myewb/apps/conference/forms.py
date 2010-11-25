"""myEWB conference registration forms

This file is part of myEWB
Copyright 2009 Engineers Without Borders Canada

Created on 2009-10-18
@author Francis Kung
"""

from datetime import date
from decimal import Decimal
from django import forms
from django.contrib.auth.models import User
from django.contrib.formtools.preview import FormPreview
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from emailconfirmation.models import EmailAddress

from communities.models import Community
from conference.constants import *
from conference.models import ConferenceRegistration, ConferenceCode, AlumniConferenceCode, QuasiVIPCode, InvalidCode
from conference.utils import needsToRenew
from creditcard.models import CC_TYPES, Product
from creditcard.forms import CreditCardNumberField, CreditCardExpiryField, PaymentFormPreview
from profiles.models import MemberProfile
from siteutils.forms import CompactAddressField
from siteutils.models import Address

class ConferenceRegistrationForm(forms.ModelForm):
    theuser = None

    # bleh.  i don't like putting so much UI text here, instead of in a template!!
    headset = forms.BooleanField(label='Headset requested?',
								 required=False,
								 help_text='Would you use a simultaneous-translation headset for keynote speakers not in your preferred language, if headsets were available?')
	
    foodPrefs = forms.ChoiceField(label='Food preferences',
								  choices=FOOD_CHOICES,
								  widget=forms.RadioSelect,
								  initial='none',
								  help_text='Please use the text area below to provide details or any other requirements, if needed')
    specialNeeds = forms.CharField(label='Special needs',
								   required=False,
								   widget=forms.Textarea,
								   help_text='Please let us know about any special dietary, accessibility or other needs you may have, or any medical conditions (including allergies).')
    
    emergName = forms.CharField(label='Emergency contact name')
    emergPhone = forms.CharField(label='Emergency contact phone number')
    
    prevConfs = forms.ChoiceField(label='EWB national conferences attended',
								  choices=PASTEVENTS)
    prevRetreats = forms.ChoiceField(label='EWB regional retreats attended',
									 choices=PASTEVENTS)
    
    resume = forms.FileField(label='Resume',
                             required=False,
                             help_text="(optional) Attach a resume if you would like it shared with our sponsors")
    
    cellphone = forms.CharField(label='Cell phone number',
                                required=False,
                                help_text="(optional) If you wish to receive logistical updates and reminders by text message during the conference")

    grouping = forms.ChoiceField(label='Which group do you belong to?',
                                 choices=EXTERNAL_GROUPS,
                                 required=False)
    grouping2 = forms.CharField(label='&nbsp;',
                                required=False,
                                help_text='(if other)')
    
    code = forms.CharField(label='Registraton code',
                           help_text='if you have a registration code, enter it here for a discounted rate.',
                           required=False)
    type = forms.ChoiceField(label='Registration type',
							 choices=ROOM_CHOICES,
							 widget=forms.RadioSelect,
							 help_text="""<a href='#' id='confoptiontablelink'>click here for a rate guide and explanation</a>""")
    
    africaFund = forms.ChoiceField(label='Support an African delegate?',
                                   choices=AFRICA_FUND,
                                   initial='75',
								   required=False,
								   help_text='<a href="/site_media/static/conference/delegateinfo.html" class="delegatelink">more information...</a>')

    ccardtype = forms.ChoiceField(label='Credit card type',
								  choices=CC_TYPES)
    cc_number = CreditCardNumberField(label='Credit card number')
    cc_expiry = CreditCardExpiryField(label='Credit card expiry',
                                      help_text='MM/YY')
    billing_name = forms.CharField(label='Name on credit card', max_length=255)
    address = CompactAddressField(label='Billing Address')
        
    # this gets set if the card is declined at the bank
    trnError = None

    class Meta:
        model = ConferenceRegistration
        fields = ['headset', 'foodPrefs', 'specialNeeds', 'emergName', 'emergPhone',
                  'prevConfs', 'prevRetreats', 'resume', 'cellphone', 
                  'code', 'type', 'africaFund']

    def clean_code(self):
        codestring = self.cleaned_data['code'].strip().lower()
        
        if not codestring:
            return None
        
        try:
            if (codestring == 'ewbalumni'):
                code = AlumniConferenceCode()
            elif (codestring == 'ewbconfspecial'):
                code = QuasiVIPCode()
            else:
                code = ConferenceCode.objects.get(code=codestring)
                
            if code.isAvailable():
                self.cleaned_data['code'] = code
                return self.cleaned_data['code']
            else:
                raise forms.ValidationError("Registration code has already been used or has expired")
        except ObjectDoesNotExist:
            raise forms.ValidationError("Invalid registration code")
        
    def clean_africaFund(self):
        if self.cleaned_data['africaFund']:
            if self.cleaned_data['africaFund'].strip() == '':
                self.cleaned_data['africaFund'] = None
        else:
            self.cleaned_data['africaFund'] = None
                
        return self.cleaned_data['africaFund']

    def clean(self):
        # If the card is declined at the bank, trnError will get set...
        if self.trnError:
            raise forms.ValidationError("Credit card error: " + self.trnError)
        
        if self.errors:
            return None

        # and do some auto-processing as needed
        cleaned_data = self.cleaned_data
        cleaned_data['products'] = []
        total_cost = 0
        
        if not cleaned_data.get('prevConfs', None):
            cleaned_data['prevConfs'] = 0
        if not cleaned_data.get('prevRetreats', None):
            cleaned_data['prevRetreats'] = 0
        if not cleaned_data.get('code', None):
            cleaned_data['code'] = None
            
        if not cleaned_data.get('grouping', None):
            cleaned_data['grouping'] = None
        if cleaned_data['grouping'] == 'Other' and cleaned_data.get('grouping2', None):
            cleaned_data['grouping'] = cleaned_data['grouping2'] 
            
        if cleaned_data['code']:
            codename = cleaned_data['code'].getShortname()
        else:
            codename = "open"
        
        sku = "confreg-2011-" + cleaned_data['type'] + "-" + codename
        
        if not CONF_OPTIONS.get(sku, None):
            errormsg = "The registration code you've entered is not valid for the registration type you selected."
            self._errors['type'] = self.error_class([errormsg])
            self._errors['code'] = self.error_class([errormsg])
            del cleaned_data['type']
            del cleaned_data['code']
            raise forms.ValidationError("Unable to complete registration (see errors below)")
         
        cost = CONF_OPTIONS[sku]['cost']
        name = CONF_OPTIONS[sku]['name']
        product, created = Product.objects.get_or_create(sku=sku)
        if created:
            product.name = name
            product.amount = cost
            product.save()
            
        cleaned_data['products'].append(product.sku)
        total_cost = total_cost + Decimal(product.amount)

        if needsToRenew(self.user.get_profile()):
            # FIXME: some duplicated code from profiles.forms (where saving membership fees)
            if self.user.get_profile().student():
                type = "studues"
            else:
                type = "produes"

            chapter = self.user.get_profile().get_chapter()
            if chapter:
                type += "-" + chapter.slug
                chaptername = " (%s)" % chapter.name
            else:
                chaptername = ""
            
            product, created = Product.objects.get_or_create(sku=type)
            if created:
                if self.user.get_profile().student():
                    product.amount = "20.00"
                    product.name = "Student membership" + chaptername
                    product.save()
                else:
                    product.amount = "40.00"
                    product.name = "Professional membership" + chaptername
                    product.save()
            
            cleaned_data['products'].append(product.sku)
            total_cost = total_cost + Decimal(product.amount)

        if cleaned_data['africaFund']:
            cost = cleaned_data['africaFund']
            sku = "11-africafund-" + cost
            name = "Support an African delegate ($" + cost + ")"
            product, created = Product.objects.get_or_create(sku=sku)
            if created:
                product.name = name
                product.amount = cost
                product.save()
            
            cleaned_data['products'].append(product.sku)
            total_cost = total_cost + Decimal(product.amount)

        cleaned_data['total_cost'] = total_cost
        self.cleaned_data = cleaned_data

        return self.cleaned_data
    
    _user = None
    def _get_user(self):
        return self._user
    
    def _set_user(self, value):
        self._user = value
        if self.fields.get('address', None):
            self.fields['address'].user = value
        if value.is_bulk:
            del(self.fields['prevConfs'])
            del(self.fields['prevRetreats'])
            #del(self.fields['code'])
            self.fields['type'].choices=EXTERNAL_CHOICES
        else:
            del(self.fields['grouping'])
            del(self.fields['grouping2'])
            
    user = property(_get_user, _set_user)

class ConferenceRegistrationFormPreview(PaymentFormPreview):
    preview_template = 'conference/preview.html'
    form_template = 'conference/registration.html'
    username = None
    
    def done(self, request, cleaned_data):
        # add profile info, as it's needed for CC processing
        form = self.form(request.POST)
        if not request.user.email:

            # simulate a cred card declined, to trigger form validation failure
            response = (False, "Please edit your myEWB profile and enter an email address.")

        else:
            cleaned_data['email'] = request.user.email
            if request.user.get_profile().default_phone() and request.user.get_profile().default_phone().number:
                cleaned_data['phone'] = request.user.get_profile().default_phone().number
            else:
                cleaned_data['phone'] = '416-481-3696'
            
            # this call sends it to the bank!!
            response = super(ConferenceRegistrationFormPreview, self).done(request, cleaned_data)
        
        if response[0] == True:
            if cleaned_data['code']:
                codename = cleaned_data['code'].getShortname()
            else:
                codename = "open"
            
            registration = form.save(commit=False)
            registration.user = request.user
            registration.type = "confreg-2011-" + cleaned_data['type'] + "-" + codename
            registration.amountPaid = CONF_OPTIONS[registration.type]['cost']
            registration.roomSize = cleaned_data['type']
            if cleaned_data['code']:
                registration.code = cleaned_data['code']
            else:
                registration.code = None
            registration.receiptNum = response[2]
            registration.txid = response[1]
            
            if cleaned_data.get('grouping', None):
                registration.grouping = cleaned_data['grouping']
            
            registration.save()
            
            # and update their membership if they paid it
            if needsToRenew(request.user.get_profile()):
                request.user.get_profile().pay_membership()
                
            # lastly, add them to the group
            grp, created = Community.objects.get_or_create(slug='conference2011',
                                                           defaults={'invite_only': True,
                                                                     'name': 'National Conference 2011 delegates',
                                                                     'creator': request.user,
                                                                     'description': 'National Conference 2011 delegates',
                                                                     'mailchimp_name': 'National Conference 2011',
                                                                     'mailchimp_category': 'Conference'})
            grp.add_member(request.user)
            
            
            # don't do the standard render_to_response; instead, do a redirect
            # so that someone can't double-submit by hitting refresh
            return HttpResponseRedirect(reverse('confreg'))
        
        else:
            registration = None
            form.trnError = response[1]
            form.clean

        return render_to_response('conference/registration.html',
                                  {'registration': registration,
                                   'form': form
                                   },
                                   context_instance=RequestContext(request)
                                   )

class CodeGenerationForm(forms.Form):
    type = forms.CharField(max_length=1, label='Type of code')
    start = forms.IntegerField(label='Starting at')
    number = forms.IntegerField(label='How many codes')
    
class ConferenceSignupForm(forms.Form):

    firstname = forms.CharField(label="First name")
    lastname = forms.CharField(label="Last name")
    email = forms.EmailField(label = "Email", required = True, widget = forms.TextInput())
    gender = forms.ChoiceField(choices=MemberProfile.GENDER_CHOICES,
                               widget=forms.RadioSelect,
                               required=True)
    language = forms.ChoiceField(label="Preferred language",
                                 choices=MemberProfile.LANG_CHOICES,
                                 widget=forms.RadioSelect,
                                 required=True)
    
    def clean_email(self):
        other_emails = EmailAddress.objects.filter(email__iexact=self.cleaned_data['email'])
        verified_emails = other_emails.filter(verified=True)
        if verified_emails.count() > 0:
            raise forms.ValidationError("This email address has already been used. Please sign in or use a different email.")
        
        # this is probably redundant, but just to be sure...
        users = User.objects.filter(email=self.cleaned_data['email'], is_bulk=False)
        if users.count():
            raise forms.ValidationError("This email address has already been used. Please sign in or use a different email.")
        
        return self.cleaned_data['email']

    def save(self):
        firstname = self.cleaned_data['firstname']
        lastname = self.cleaned_data['lastname']
        email = self.cleaned_data["email"]
        
        try:
            new_user = User.objects.get(email=email, is_bulk=1)
        except User.DoesNotExist:
            new_user = User.extras.create_bulk_user(email)
            
        profile = new_user.get_profile()
        profile.first_name = firstname
        profile.last_name = lastname
        profile.gender = self.cleaned_data['gender']
        profile.language = self.cleaned_data['language']
        profile.save()
        
        new_user.first_name = firstname
        new_user.last_name = lastname
        password = User.objects.make_random_password()
        new_user.set_password(password)
        new_user.save()
        
        return new_user.username, password # required for authenticate()
