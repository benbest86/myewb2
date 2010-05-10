import pycountry
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
#from profiles.models import Profile
from siteutils.countries import CountryField

class ServiceProvider(models.Model):
  PROVIDER_CHOICES = (
      ('airline', _('Airline')),
      ('insurance', _('Insurance')),
      ('emergency_contact', _('Emergency Contact')),
      ('partner_organization', _('Partner Organization')),
  )
  type = models.CharField(_('type'), max_length=100, choices=PROVIDER_CHOICES, null=True, blank=True)
  first_name = models.CharField(_('first name(s)'), max_length=100, blank=True)
  last_name = models.CharField(_('last name'), max_length=100, blank=True)
  company_name = models.CharField(blank=True, max_length=100)

  addresses = generic.GenericRelation("Address")
  phone_numbers = generic.GenericRelation("PhoneNumber")


  def __unicode__(self):
    if len(self.company_name):
      return self.company_name
    else:
      full_name = "%s %s" % (self.first_name, self.last_name)
      if len(full_name) > 1:
        return full_name

    return "<no name>"


class PhoneNumber(models.Model):
  content_type = models.ForeignKey(ContentType)
  object_id = models.PositiveIntegerField()
  content_object = generic.GenericForeignKey()

  PHONE_LABELS = (
      ('Mobile', _('Mobile')),
      ('Home', _('Home')),
      ('Work', _('Work')),
      ('School', _('School')),
      ('Work Fax', _('Work Fax')),
      ('Home Fax', _('Home Fax')),
      ('Cottage', _('Cottage')),
      ('Parents', _('Parents')),
      ('Placement', _('Placement')),
      ('Other', _('Other'))
  )
  
  # want a combo box for this -- choices/custom
  label = models.CharField(_('number type'), max_length=255, choices=PHONE_LABELS, null=True, blank=True)
  number = models.CharField(_('phone number'), max_length=255, null=True, blank=True)

  def __unicode__(self):
    return "%s: %s" % (self.label, self.number)

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
provinces.append(('', 'None / Other'))
        
countries2 = list(pycountry.countries)
countries = []
for c in countries2:
    countries.append((c.alpha2, c.name))

class Address(models.Model):
  content_type = models.ForeignKey(ContentType)
  object_id = models.PositiveIntegerField()
  content_object = generic.GenericForeignKey()
  
  label = models.CharField(max_length=255, null=False, blank=False)
  street = models.CharField(_('street address'), max_length=255, null=True, blank=True)
  city = models.CharField(_('city'), max_length=255, null=True, blank=True)
  province = models.CharField(_('province / state'), max_length=2, choices=provinces, default='AB', blank=True)
  postal_code = models.CharField(_('postal / zip code'), max_length=255, null=True, blank=True)
  country = CountryField(_('country'), max_length=2, choices=countries, default='CA')
  
  # FIXME -- have a smarter fallback name for the 
  def __unicode__(self):
    if self.content_type.name == "member profile":
      owner = self.content_type.name
    elif self.content_type.name == "service provider":
      owner = self.content_type.name
    else:
      owner = "<orphan>"
    return u"%s: %s: %s, %s" % (owner, self.label, self.city, self.province)

