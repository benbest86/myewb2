"""myEWB profile models
Models to store site-specific profile information.

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2009-06-22
Last modified: 2009-07-31
@author: Joshua Gorner, Francis Kung, Ben Best
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.utils.translation import ugettext_lazy as _

from emailconfirmation.models import EmailAddress

from pinax.apps.profiles.models import Profile, create_profile
from networks import emailforwards
from networks.models import Network
from countries import COUNTRIES
from datetime import date

class MemberProfileManager(models.Manager):
    def get_from_view_args(self, *args, **kwargs):
        username = kwargs.get('username', None) or (len(args) > 0 and args[0])
        if username:
            user = User.objects.get(username=username)
            try:
                return MemberProfile.objects.get(user__id=user.id)
            except MemberProfile.DoesNotExist:
                pass
        return None

class MemberProfile(Profile):
    """ Extends Pinax's Profile object to provide additional information stored in the previous myEWB application.
    
    Note that Django and/or Pinax already handle language, email addresses, and 'additional info'.
    """
    
    # This will be copied to the respective fields in the User object
    first_name = models.CharField(_('first name(s)'), max_length=30, blank=True)
    preferred_first_name = models.CharField(_('preferred first name (if different)'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    
    country = models.CharField(_('country'), max_length=2, choices=COUNTRIES, null=True, blank=True)
    
    street_address = models.CharField(_('street address'), max_length=50, null=True, blank=True)
    street_address_two = models.CharField(_('street address line 2'), max_length=50, null=True, blank=True)
    city = models.CharField(_('city'), max_length=40, null=True, blank=True)
    province = models.CharField(_('province / state (abbreviation)'), max_length=10, null=True, blank=True)
    postal_code = models.CharField(_('postal / zip code'), max_length=16, null=True, blank=True)
    
    # PhoneNumberField is not suitable since we need to allow non-North American numbers
    home_phone_number = models.CharField(_('home phone number'), max_length=40, null=True, blank=True)
    mobile_phone_number = models.CharField(_('mobile phone number'), max_length=40, null=True, blank=True)
    work_phone_number = models.CharField(_('work phone number'), max_length=40, null=True, blank=True)
    alt_phone_number = models.CharField(_('alternate phone number'), max_length=40, null=True, blank=True)
    fax_number = models.CharField(_('fax number'), max_length=40, null=True, blank=True)
    
    GENDER_CHOICES = (
        ('M', _('Male')),
        ('F', _('Female')),
    )
    gender = models.CharField(_('gender'), max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    # student = models.BooleanField(_('student'), null=True, blank=True)        # see below
    membership_expiry = models.DateField(_('membership expiry'), null=True, blank=True)
    
    current_login = models.DateTimeField(_('current login'), null=True, blank=True)
    login_count = models.IntegerField(_('login count'), null=True, blank=True)
    
    show_emails = models.BooleanField(_('show emails'), null=True, blank=True)
    show_replies = models.BooleanField(_('show replies'), null=True, blank=True)
    sort_by_last_reply = models.BooleanField(_('sort by last reply'), null=True, blank=True)
    address_updated = models.DateField(_('address updated'), null=True, blank=True)
    replies_as_emails = models.BooleanField(_('replies as emails'), null=True, blank=True)

    objects = MemberProfileManager()
    
    def in_canada(self):
        return self.country == "CA"
    
    def email_addresses(self):
        return EmailAddress.objects.filter(verified=True, user=self.user)
    
    def save(self, force_insert=False, force_update=False):
        if self.first_name or self.last_name:
            # Because nothing is set, this block should NOT be called on the save resulting from create_member_profile
            # If it does it could cause recursion problems
            self.user.first_name = self.first_name
            self.user.last_name = self.last_name
            self.user.save()
        
        if self.preferred_first_name:
            if self.last_name:
                self.name = self.preferred_first_name + " " + self.last_name
            else:
                self.name = self.preferred_first_name
        elif self.first_name:
            if self.last_name:
                self.name = self.first_name + " " + self.last_name
            else:
                self.name = self.first_name
        elif self.last_name:
            self.name = self.last_name
        else:
            self.name = None
                
        self.location = self.city
        if self.province:
            self.location += ", "
            self.location += self.province
            
        return models.Model.save(self, force_insert, force_update)
            
    def student(self):
        """Determine whether the instant user is a student based on the user's student records"""
        student_records = StudentRecord.objects.filter(user=self.user)
        today = date.today()
        for record in student_records:
            # If no start date listed, assume student unless end date is listed and past end date. 
            # If start date (before today) listed but no end date, assume student.
            # Otherwise, deem student only if between start and end dates.
            # For greater clarity, if neither date is listed, assume student.
            if (record.start_date is None or record.start_date <= today) \
                    and (record.graduation_date is None or record.graduation_date >= today):
                return True
        return False

    def is_owner(self, user):
        """
        Determine whether or not a given user owns this profile.
        @params: user - user object
        @returns: True if user is the profile owner, False otherwise
        """
        return (user.id == self.user.id)
    
    # add a year of membership: either starting today if last membership
    # is already expired, or a year after the current membership expires
    def pay_membership(self):
        if self.membership_expiry == None or self.membership_expiry < date.today():
            self.membership_expiry = date.today()
            
        self.membership_expiry = date(self.membership_expiry.year + 1,
                                      self.membership_expiry.month,
                                      self.membership_expiry.day)
        self.save()

def create_member_profile(sender, instance=None, **kwargs):
    """Automatically creates a MemberProfile for a new User."""
    if instance is None:
        return
    profile, created = MemberProfile.objects.get_or_create(user=instance)

post_save.disconnect(create_profile, sender=User)
post_save.connect(create_member_profile, sender=User)

def set_primary_email(sender, instance=None, **kwargs):
    """
    Automatically sets a verified email to primary if no verified address exists yet.
    Also updates LDAP for email forwards if the primary emai
    """
    if instance is not None and instance.verified:
        user = instance.user
        if instance.primary == False:
            # if we only have one email it is this one
            if user.emailaddress_set.count() == 1:
                instance.set_as_primary()
                emailforwards.updateUser(user, instance.email)
        else:
            emailforwards.updateUser(user, instance.email)

post_save.connect(set_primary_email, sender=EmailAddress)
    
class StudentRecordManager(models.Manager):
    def get_from_view_args(self, *args, **kwargs):
        username = kwargs.get('username') or (len(args) > 0 and args[0])
        id = kwargs.get('student_record_id', None) or kwargs.get('record_id', None) or (len(args) > 1 and args[1])
        if id and username:
            try:
                return StudentRecord.objects.get(pk=id, user__username=username)
            except StudentRecord.DoesNotExist:
                pass
        return None

class StudentRecord(models.Model):
    """ Represents a record of a member's current or past attendance at a university or other educational institution.
    A member may have one or more such records.
    """
    
    user = models.ForeignKey(User, verbose_name=_('user'))
    network = models.ForeignKey(Network, verbose_name=_('network'))
    
    institution = models.CharField(_('institution'), max_length=50, null=True, blank=True)
    student_number = models.IntegerField(_('student number'), null=True, blank=True)
    field = models.CharField(_('field'), max_length=40, null=True, blank=True)
    
    STUDENT_LEVELS = (
        ('HS', _('High school')),
        ('CL', _('College')),
        ('UG', _('Undergraduate')),
        ('GR', _('Graduate')),
        ('OT', _('Other')),
    )
    level = models.CharField(_('level'), max_length=2, choices=STUDENT_LEVELS, null=True, blank=True)
    start_date = models.DateField(_('start date'), null=True, blank=True)
    graduation_date = models.DateField(_('graduation date'), null=True, blank=True)
    
    objects = StudentRecordManager()

    def is_owner(self, user):
        """
        Determine whether or not a given user owns this record.
        @params: user - user object
        @returns: True if user is the profile owner, False otherwise
        """
        return (user.id == self.user_id)

class WorkRecordManager(models.Manager):
    def get_from_view_args(self, *args, **kwargs):
        username = kwargs.get('username', None) or (len(args) > 0 and args[0])
        id = kwargs.get('work_record_id', None) or kwargs.get('record_id', None) or (len(args) > 1 and args[1])
        if id and username:
            try:
                return WorkRecord.objects.get(pk=id, user__username=username)
            except WorkRecord.DoesNotExist:
                pass
        return None

class WorkRecord(models.Model):
    """ Represents a record of a member's current or past employment. A member may have one or more such records.
    """
    
    user = models.ForeignKey(User, verbose_name=_('user'))
    network = models.ForeignKey(Network, verbose_name=_('network'))
    
    employer = models.CharField(_('employer'), max_length=50, null=True, blank=True)
    sector = models.CharField(_('sector'), max_length=40, null=True, blank=True)
    position = models.CharField(_('position'), max_length=50, null=True, blank=True)
    start_date = models.DateField(_('start date'), null=True, blank=True)
    end_date = models.DateField(_('end date'), null=True, blank=True)
    
    COMPANY_SIZES = (
        ('tiny', _('1 - 5 employees')),
        ('small', _('6 - 20 employees')),
        ('medium', _('21 - 100 employees')),
        ('large', _('over 100 employees')),
    )
    company_size = models.CharField(_('company size'), max_length=10, choices=COMPANY_SIZES, null=True, blank=True)
    
    INCOME_LEVELS = (
        ('low', _('under $30,000')),
        ('lower_mid', _('$30,000 to $45,000')),
        ('upper_mid', _('$45,000 to $75,000')),
        ('high', _('over $75,000')),
    )
    income_level = models.CharField(_('income level'), max_length=10, choices=INCOME_LEVELS, null=True, blank=True)
    
    objects = WorkRecordManager()
    
    def is_owner(self, user):
        """
        Determine whether or not a given user owns this record.
        @params: user - user object
        @returns: True if user is the profile owner, False otherwise
        """
        return (user.id == self.user_id)
