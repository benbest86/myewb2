"""myEWB networks models declarations

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Last modified on 2009-07-29
@author Joshua Gorner, Benjamin Best
"""

from django.core.urlresolvers import reverse
from django.contrib.auth.models import  User
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.signals import post_save

from base_groups.models import BaseGroup, GroupMember, GroupLocation, add_creator_to_group
from networks import emailforwards

class Network(BaseGroup):
    
    TYPE_CHOICES = (
	    ('N', _('National')),
        ('R', _('Regional')),
        ('U', _('University')),
        ('C', _('Company')),
    )
    network_type = models.CharField(_('network type'), max_length=1, null=True, blank=True, choices=TYPE_CHOICES)
    
    def get_absolute_url(self):
        return reverse('network_detail', kwargs={'group_slug': self.slug})
        
    def save(self, force_insert=False, force_update=False):
        self.model = "Network"
        return super(Network, self).save(force_insert, force_update)
        
    def is_chapter(self):
        return hasattr(self, "chapter_info")
        
    class Meta:
        verbose_name_plural = "networks"
    
class ChapterInfo(models.Model):
    network = models.OneToOneField(Network, related_name="chapter_info", verbose_name=_('network'))
    
    # chapter name is not necessarily predictable, e.g. "Grand River Professional Chapter" for Kitchener-Waterloo
    chapter_name = models.CharField(_('chapter name'), max_length=500)
        
    street_address = models.CharField(_('street address'), max_length=50)
    street_address_two = models.CharField(_('street address line 2'), max_length=50, null=True, blank=True)
    city = models.CharField(_('city'), max_length=40)
    province = models.CharField(_('province'), max_length=10)
    postal_code = models.CharField(_('postal code'), max_length=16)
    phone = models.CharField(_('telephone number'), max_length=40, null=True, blank=True)
    fax = models.CharField(_('fax number'), max_length=40, null=True, blank=True)
    
    student = models.BooleanField(_('student chapter?'), default=True)
    
def create_network_location(sender, instance=None, **kwargs):
    """Automatically creates a GroupLocation for a new Network."""
    if instance is None or instance.id is None:
        return
    location, created = GroupLocation.objects.get_or_create(group=instance)

post_save.connect(create_network_location, sender=Network)

class EmailForward(models.Model):
    network = models.ForeignKey(Network, related_name="email_forwards", verbose_name=_('network'))
    user = models.ForeignKey(User, related_name="email_forwards", verbose_name=_('user'))
    address = models.EmailField(unique=True)

    def save(self, force_insert=False, force_update=False):
        emailforwards.addAddress(self.user, self.address)
        super(EmailForward, self).save(force_insert, force_update)

    def delete(self):
        emailforwards.removeAddress(self.user, self.address)
        super(EmailForward, self).delete()
        

def add_users_to_default_networks(sender, instance=None, created=False, **kwargs):
    if created:
        try:
            ewb = Network.objects.get(slug='ewb')
            ewb.add_member(instance)
        except Network.DoesNotExist:
            pass
post_save.connect(add_users_to_default_networks, sender=User)
# use same add_creator_to_group from base_groups
post_save.connect(add_creator_to_group, sender=Network)
