"""myEWB conference registration forms

This file is part of myEWB
Copyright 2009 Engineers Without Borders Canada

Created on 2009-10-18
@author Francis Kung
"""

from datetime import date
from django import forms
from django.contrib.formtools.preview import FormPreview
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from conference.constants import *
from conference.models import ConferenceRegistration, ConferenceCode, InvalidCode
from conference.utils import needsToRenew
from creditcard.models import CC_TYPES, Product
from creditcard.forms import CreditCardNumberField, CreditCardExpiryField, PaymentFormPreview

class ConferenceRegistrationForm(forms.ModelForm):
    theuser = None
	
    # TODO: find list of chapters a user is in, and present a drop-down if 
    # they are apart of multiple ones?  maybe?
	#chapters = [('none', _('(none)'))]
    #chapter = forms.ChoiceField(choices=chapters)

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
    
    type = forms.ChoiceField(label='Registration type',
							 choices=ROOM_CHOICES,
							 widget=forms.RadioSelect,
							 help_text="""<table border='1' class='descform'>
  <tr>
    <th>&nbsp;</th>
    <th>Quad room</th>
    <th>Double room</th>
    <th>Single room</th>
    <th>No room</th>
  </tr>
  <tr>
    <th>University chapters: Manitoba - BC</th>
    <td>$175</td>    
    <td>$305</td>    
    <td>$565</td>    
    <td>$140</td>    
  </tr>
  <tr>
    <th>University chapters: Nova Scotia - Ontario</th>
    <td>$250</td>    
    <td>$380</td>    
    <td>$645</td>    
    <td>$215</td>    
  </tr>
  <tr>
    <th>University chapters: Newfoundland</th>
    <td>$500</td>    
    <td>$630</td>    
    <td>$890</td>    
    <td>$460</td>    
  </tr>
  <tr>
    <th>City chapters: Manitoba - BC</th>
    <td>$400</td>    
    <td>$530</td>    
    <td>$660</td>    
    <td>$300</td>    
  </tr>
  <tr>
    <th>City chapters: Nova Scotia - Ontario</th>
    <td>$475</td>    
    <td>$605</td>    
    <td>$735</td>    
    <td>$380</td>    
  </tr>
</table>""")
    
    code = forms.CharField(label='Registraton code',
						   help_text='please enter the registration code sent to you by your chapter president. Note that registration codes are required this year.')
    africaFund = forms.BooleanField(label='Support an African delegate?',
								    required=False,
								    help_text='check to contribute an additional $20 (non-refundable) towards a fund to bring young African leaders to the conference as delegates.')

    ccardtype = forms.ChoiceField(label='Credit card type',
								  choices=CC_TYPES)
    billing_name = forms.CharField(label='Name on credit card', max_length=255)
    cc_number = CreditCardNumberField(label='Credit card number')
    cc_expiry = CreditCardExpiryField(label='Credit card expiry',
                                      help_text='MM/YY')
        
    challenge = forms.CharField(label='Your answer',
							    widget=forms.Textarea)
    malawiwatsan = forms.ChoiceField(label='Water and Sanitation in Malawi',
									 choices=OVRANK)
    malawiagric =  forms.ChoiceField(label='Agriculture in Zambia/Malawi',
									 choices=OVRANK)
    ghanaagric = forms.ChoiceField(label='Agriculture in Ghana',
								   choices=OVRANK)
    burkinaagric = forms.ChoiceField(label='Agriculture in Ghana',
									 choices=OVRANK)
    ghanagari = forms.ChoiceField(label='Good Governance in Ghana',
								  choices=OVRANK)

    # this gets set if the card is declined at the bank
    trnError = None

    class Meta:
		model = ConferenceRegistration
		exclude = ('user', 'amountPaid', 'roomSize', 'type', 'date', 
				   'cancelled', 'receiptNum', 'chapter', 'txid')

    def clean_code(self):
        codestring = self.cleaned_data['code'].strip().lower()

        try:
            code = ConferenceCode.objects.get(code=codestring)
                
            if code.isAvailable():
                self.cleaned_data['code'] = code
                return self.cleaned_data['code']
            else:
                raise forms.ValidationError("Registration code has already been used or has expired")
        except ObjectDoesNotExist:
            raise forms.ValidationError("Invalid registration code")

    def clean(self):
        # If the card is declined at the bank, trnError will get set...
        if self.trnError:
            raise forms.ValidationError(self.trnError)
        return self.cleaned_data

class ConferenceRegistrationFormPreview(PaymentFormPreview):
    preview_template = 'conference/preview.html'
    form_template = 'conference/registration.html'
    
    def done(self, request, cleaned_data):
        
        cleaned_data['products'] = []
        
        sku = "confreg-2010-" + cleaned_data['type'] + "-" + cleaned_data['code'].getShortname()
        cost = CONF_OPTIONS[sku]['cost']
        name = CONF_OPTIONS[sku]['name']
        product, created = Product.objects.get_or_create(sku=sku)
        if created:
            product.name = name
            product.amount = cost
            product.save()
            
        cleaned_data['products'].append(product.sku)

        if needsToRenew(request.user.get_profile()):
            # FIXME: some duplicated code from profiles.forms (where saving membership fees)
            if request.user.get_profile().student():
                type = "studues"
            else:
                type = "produes"

            # TODO: a better way of determining someone's (home) chapter!
            # (right now we just pick the first one... not that great...
            chapters = ChapterInfo.objects.all()
            chapters.filter(network__members__user=request.user)
            if chapters.count > 0:
                type += "-" + chapters[0].group.slug
                chaptername = " (%s)" % chapter.chapter_name
            else:
                chaptername = ""
            
            product, created = Product.objects.get_or_create(sku=type)
            if created:
                if request.user.get_profile().student():
                    product.amount = "20.00"
                    product.name = "Student membership" + chaptername
                    product.save()
                else:
                    product.amount = "40.00"
                    product.name = "Professional membership" +  + chaptername
                    product.save()
            
            cleaned_data['products'].append(product.sku)

        if cleaned_data['africaFund'] == True:
            sku = "09-africafund"
            cost = "20"
            name = "$20 to support an African delegate"
            product, created = Product.objects.get_or_create(sku=sku)
            if created:
                product.name = name
                product.amount = cost
                product.save()
            
            cleaned_data['products'].append(product.sku)
            
        # add profile info, as it's needed for CC processing
        form = self.form(request.POST)
        if not request.user.email or \
            not request.user.get_profile().home_phone_number or \
            not request.user.get_profile().street_address or \
            not request.user.get_profile().city or \
            not request.user.get_profile().province or \
            not request.user.get_profile().postal_code or \
            not request.user.get_profile().country:

            # simulate a cred card declined, to trigger form validation failure
            response = (False, "Please fill out your profile information.")

        else:
            cleaned_data['email'] = request.user.email
            cleaned_data['phone'] = request.user.get_profile().home_phone_number
            cleaned_data['billing_address1'] = request.user.get_profile().street_address
            cleaned_data['billing_address2'] = request.user.get_profile().street_address_two
            cleaned_data['billing_city'] = request.user.get_profile().city
            cleaned_data['billing_province'] = request.user.get_profile().province
            cleaned_data['billing_postalcode'] = request.user.get_profile().postal_code
            cleaned_data['billing_country'] = request.user.get_profile().country
        
            # this call sends it to the bank!!
            response = super(ConferenceRegistrationFormPreview, self).done(request, cleaned_data)
        
        if response[0] == True:
            registration = form.save(commit=False)
            registration.user = request.user
            registration.type = "confreg-2010-" + cleaned_data['type'] + "-" + cleaned_data['code'].getShortname()
            registration.amountPaid = CONF_OPTIONS[registration.type]['cost']
            registration.roomSize = cleaned_data['type'][:1]
            registration.code = cleaned_data['code']
            registration.receiptNum = response[2]
            registration.txid = response[1]
            
            registration.save()
            
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
    
