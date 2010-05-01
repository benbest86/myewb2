"""myEWB credit card forms

Some of this code comes from the good people at
http://www.djangosnippets.org/snippets/764/

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2009-08-11
Last modified: 2009-08-12
@author: Francis Kung
"""

import re, datetime, time, urllib, pycountry
from django import forms
from django.contrib.auth.models import User
from django.contrib.formtools.preview import FormPreview
from django.core.mail import EmailMessage
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.utils.safestring import mark_safe
from apps.creditcard.utils import *
from apps.creditcard.models import Payment, Product
from siteutils.forms import AddressField
from siteutils.models import Address

from uni_form.helpers import FormHelper, Submit, Reset
from uni_form.helpers import Layout, Fieldset, Row, HTML
import settings
from datetime import datetime

class CreditCardNumberField(forms.CharField):
    """ A forms widget for a creditcard number """
    def clean(self, value):
        
        value = forms.CharField.clean(self, value)
        if not ValidateCharacters(value):
            raise forms.ValidationError('Can only contain numbers and spaces.')
        value = StripToNumbers(value)
        if not ValidateLuhnChecksum(value):
            raise forms.ValidationError('Not a valid credit card number.')
        
        return value


class CreditCardExpiryField(forms.CharField):
    """ A forms widget for a creditcard expiry date """
    def clean(self, value):     
        value = forms.CharField.clean(self, value)
        
        # Just check MM/YY Pattern
        r = re.compile('^([0-9][0-9])/([0-9][0-9])$')
        m = r.match(value)
        if m == None:
            raise forms.ValidationError('Must be in the format MM/YY. i.e. "11/10" for Nov 2010.')
        
        # Check that the month is 1-12
        month = int(m.groups()[0])
        if month < 1 or month > 12:
            raise forms.ValidationError('Month must be in the range 1 - 12.')
        
        # Check that the year is not too far into the future
        year = int(m.groups()[1])
        curr_year = datetime.now().year % 100
        max_year = curr_year + 10
        if year > max_year or year < curr_year:
            raise forms.ValidationError('Year must be in the range %s - %s.' % (str(curr_year).zfill(2), str(max_year).zfill(2),))

        return value
    
class MultipleEntryField(forms.MultipleChoiceField):
    """ Just like MultipleChoiceField, except that all choices are always selected.
    Not used right now; was from my attempt to put multiple products in one payment
    (but I'm giving up on that for now, after fighitng with django's forms for way too long)
    """
    def clean(self, value):
        return self.choices

class ProductWidget(forms.HiddenInput):
    """ Widget to put a product SKU in a hidden field, and display a more human-friendly
    description of it on the form
    """
    def render(self, name, value, attrs=None):
        html = super(ProductWidget, self).render(name, value, attrs)
        
        product = Product.objects.get(sku=value)
        html = "%s $%s - %s" % (html, product.amount, product.name)
        return mark_safe(html)
        
class PaymentForm(forms.ModelForm):
    _user = None    
    cc_number = CreditCardNumberField(label="Credit card number")
    cc_expiry = CreditCardExpiryField(label="Credit card expiry (mm/yy)")
#    products = MultipleEntryField(label='products',
#                    widget=forms.MultipleHiddenInput)
#                    widget=forms.CheckboxSelectMultiple(attrs={'checked':'checked',
#                                                               'disabled':'disabled'}),
#                                                               choices=[('membership', 'membership')]
#                    )
    products = forms.CharField(max_length=40,
                               label='products',
                               widget=ProductWidget)
    
    address = AddressField(label='Billing Address')
        
	# this gets set if the card is declined at the bank
    trnError = None

	# various layout stuff, using uni_form
	# (http://github.com/pydanny/django-uni-form/tree/master)
	# I don't like this, as it breaks MVC a bit, but no easy way around it
    helper = FormHelper()
    layout = Layout(
                    Fieldset('Payment details', 'products'),
                    Fieldset('Credit card information',
                             'billing_name',
                             'cc_type',
                             'cc_number',
                             'cc_expiry',
                             css_class='inlineLabels'),
                    Fieldset('Your information',
                             'address'),
                    Fieldset('',
                             'phone',
                             'email',
                             css_class='inlineLabels')
                    )
    helper.add_layout(layout)
    submit = Submit('submit', 'Preview payment')
    helper.add_input(submit)
    
    # This form is never meant to be submitted directly, but rather, use django's form preview
    # http://docs.djangoproject.com/en/dev/ref/contrib/formtools/form-preview/#ref-contrib-formtools-form-preview
    # ot requires adding a URL in whatever app you are processing payments, and setting the action here
    # (see the example in profiles.views.pay_membership and profiles.forms.MembershipPreview)
    helper.action = ''
    
    class Meta:
        model = Payment
        exclude=('billing_address1', 'billing_address2',
                 'billing_city', 'billing_province', 'billing_postalcode',
                 'billing_country')

    def _get_user(self):
        return self._user
    def _set_user(self, value):
        self.fields['address'].user = value
    user = property(_get_user, _set_user)

    def clean_address(self):
        value = self.cleaned_data['address']
        if value > 0:
            if self.user:
                #print "validating user"
                addr = Address.objects.get(pk=self.cleaned_data['address'])
                if not self.user.get_profile() == addr.content_object:
                    raise forms.ValidationError("You do not own that address!")
            #else:
            #    print "no user, skipping validation"
            return value
        else:
            raise forms.ValidationError("Please select an address")

    def clean(self):
        if self.cleaned_data:
            if len(self.cleaned_data.items()) == len(self.fields):
            
            	# Check validity of credit card
            	# (not a bank check - just a quick hash check for typos)
                the_type = self.cleaned_data.get('cc_type', '')
                number = self.cleaned_data.get('cc_number', '')
                if not ValidateCreditCard(the_type, number):
                    raise forms.ValidationError('Card Number is not a valid ' + the_type.upper() + ' card number.')

                """ No need since this has become dropdown, not free text
                # Ensure country / province match
                # TODO: be kinder to typos and short forms somehow?
                # TODO: province/state only works for CAN/USA; no one else can make a payment now...
                try:
                    country = pycountry.countries.get(alpha2=self.cleaned_data['billing_country'])
                except KeyError:
                    raise forms.ValidationError('Country is not recognized')
                
                try:
                    province = pycountry.subdivisions.get(code="%s-%s" % (country, self.cleaned_data['billing_province']))
                except KeyError:
                    raise forms.ValidationError('Province is not recognized')
                
                if not province.country == country:
                    raise forms.ValidationError('Country and province do not match')
                """
                
		# If the card is declined at the bank, trnError will get set...
        if not self.trnError == None:
            raise forms.ValidationError(self.trnError)
        return self.cleaned_data

# Not meant to be instantiated directly...!
class PaymentFormPreview(FormPreview):
    preview_template = 'creditcard/payment_preview.html'
    form_template = 'creditcard/new_payment.html'

    # username is required as a kwarg.  You're screwed if it isn't there.
    # (for displaying list of saved addresses as billing address...)
    def parse_params(self, *args, **kwargs):
        self.username = kwargs['username']
    
    def _get_form(self):
        if self.username and not self._form.user:
            self._form.user = User.objects.get(username=self.username)
        return self._form
    def _set_form(self, value):
        class FormWrapper():
            user = None
            form = None
            def __call__(self, *args, **kwargs):
                form = self.form(*args, **kwargs)
                form.user = self.user
                return form
            def _get_base_fields(self):
                return self.form.base_fields
            def _set_base_fields(self, value):
                pass
            base_fields = property(_get_base_fields, _set_base_fields)
        self._form = FormWrapper()
        self._form.form = value
    form = property(_get_form, _set_form)

    """
    def preview_post(self, request):
        self.username = request.user.username
        return super(PaymentFormPreview, self).preview_post(request)

    def post_post(self, request):
        self.username = request.user.username
        return super(PaymentFormPreview, self).post_post(request)
    """

    """
        This returns the transaction status in a roundabout way: returning
        None indicates success, and a string indicates error.  Weird, but that 
        lets us pass an error message if there was one...
    """
    def done(self, request, cleaned_data):
        
        product = Product.objects.get(sku=cleaned_data['products'])
        address = Address.objects.get(pk=cleaned_data['address'])
        if not request.user.get_profile() == address.content_object:
            return HttpResponseForbidden()
        
        # stuff necessary values into dictionary... to be encoded.
        param = {'trnCardOwner': cleaned_data['billing_name'],
                 'trnCardNumber': cleaned_data['cc_number'],
                 'trnExpMonth': cleaned_data['cc_expiry'].split('/')[0],
                 'trnExpYear': cleaned_data['cc_expiry'].split('/')[1],
                 'ordName': cleaned_data['billing_name'],
                 'ordEmailAddress': cleaned_data['email'],
                 'ordPhoneNumber': cleaned_data['phone'],
                 'ordAddress1': address.street,
                 'ordAddress2': '',
                 'ordCity':address.city,
                 'ordProvince': address.province,
                 'ordPostalCode': address.postal_code,
                 'ordCountry': address.country,
                 'prod_id_1': product.sku,
                 'prod_quantity_1': '1',
                 'prod_name_1': product.name,
                 'prod_cost_1': product.amount,
                 'trnAmount': product.amount,
                 'requestType': 'BACKEND',
                 'trnOrderNumber': 'dues-%s' % int(time.time()),
                 'merchant_id': settings.TD_MERCHANT_ID,
                }
        encoded = urllib.urlencode(param)
        
        # push the transaction to the bank
        handle = urllib.urlopen(settings.TD_MERCHANT_URL,
                                encoded)
        result = handle.read().split('&')
        
        # parse the result string back into a dictionary
        results = {}
        for r in result:
            r2 = r.split('=')
            r2[0] = urllib.unquote_plus(r2[0])
            r2[1] = urllib.unquote_plus(r2[1])
            results[r2[0]] = r2[1]
        
        # TODO: any other processing/recordkeeping we want to do?
        # do I want to save this into the db?
        
        # return based on value
        if results['trnApproved'] == '1':
            
            # send receipt
            message = loader.get_template("creditcard/receipt.html")
            c = Context({'name': cleaned_data['billing_name'],
                         'date': datetime.today(),
                         'txid': results['trnOrderNumber'],
                         'product': product.name,
                         'amount': product.amount})
            body = message.render(c)

            msg = EmailMessage(subject='Credit Card Receipt', 
                               body=body, 
                               from_email='Engineers Without Borders Canada <system@my.ewb.ca>', 
                               to=[cleaned_data['email']],
                               bcc=['monitoring@ewb.ca'],
                               )
            #msg.content_subtype = "html"
            
            msg.send(fail_silently=False)
            
            # return success
            return None
        else:
            return results['messageText']
