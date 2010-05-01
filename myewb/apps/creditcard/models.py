"""myEWB credit card models
Models to store credit card transactions.

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2009-08-11
Last modified: 2009-08-12
@author: Francis Kung, Ben Best
"""

import re, pycountry
from django.db import models
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.utils.translation import ugettext_lazy as _

from emailconfirmation.models import EmailAddress

from pinax.apps.profiles.models import Profile, create_profile
from networks.models import Network
from datetime import date

""" Thanks to http://www.djangosnippets.org/snippets/176/ """
class CurrencyField (forms.RegexField):
    currencyRe = re.compile(r'^[0-9]{1,5}(.[0-9][0-9])?$')
    def __init__(self, *args, **kwargs):
        super(CurrencyField, self).__init__(
            self.currencyRe, None, None, *args, **kwargs)

    def clean(self, value):
        value = super(CurrencyField, self).clean(value)
        return float(value)

class CurrencyInput (forms.TextInput):
    def render(self, name, value, attrs=None):
        if value != '':
            try:
                value = u"%.2f" % value
            except TypeError:
                pass
        return super(CurrencyInput, self).render(name, value, attrs)

CC_TYPES = (
    ('VI', _('Visa')),
    ('MC', _('Mastercard')),
    ('AM', _('American Express')),
#    ('DS', _('Company')),
)

provinces = []
provincelist = list(pycountry.subdivisions.get(country_code='CA'))
for p in provincelist:
    provinces.append((p.code.split('-')[1], p.name))
provinces = sorted(provinces)
provinces2 = []
provincelist = pycountry.subdivisions.get(country_code='US')
for p in provincelist:
    provinces2.append((p.code.split('-')[1], p.name))
provinces2 = sorted(provinces2)
provinces += provinces2
provinces.append(('', 'None'))
        
countries2 = list(pycountry.countries)
countries = []
for c in countries2:
    countries.append((c.alpha2, c.name))

class Payment(models.Model):
    """ Provides a base for credit card payments, including billing
    information and such.
    
    Most uses will probably extend this to add additional fields.
    """
    
    # TODO: Would be nice to pre-populate these from your profile...
    # maybe can do it via a nice javascript UI thing?
    cc_type = models.CharField(_('credit card type'), max_length=2, choices=CC_TYPES)
    cc_number = models.CharField(_('credit card number'), max_length=20)
    cc_expiry = models.DateField(_('expiry date'))

    # FIXME: so these max_length values are completely arbitrary...
    billing_name = models.CharField(_('billing name'), max_length=45)
    """
    billing_address1 = models.CharField(_('billing address'), max_length=45)
    billing_address2 = models.CharField(_('billing address 2'), max_length=45, blank=True)
    billing_city = models.CharField(_('billing city'), max_length=45)
    billing_postalcode = models.CharField(_('billing postal code'), max_length=45)
    billing_province = models.CharField(_('billing province'), max_length=2, choices=provinces, default='AB')
    billing_country = models.CharField(_('billing country'), max_length=2, choices=countries, default='CA')
    """
    phone = models.CharField(_('phone number'), max_length=45)
    email = models.EmailField(_('email address'))
    
    # well, really, many-to-one at the moment.
    products = models.ManyToManyField('Product')
    
class Product(models.Model):
    """ Items / products that you can pay for by credit card
    """
    
    name = models.CharField(_('product_name'), max_length=45)
    sku = models.CharField(_('sku'), max_length=45)
#    amount = CurrencyField(_('amount'), widget=CurrencyInput)
    # FIXME: why doesn't CurrencyField work?
    amount = models.CharField(_('amount'), max_length=20)
