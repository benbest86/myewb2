import hashlib
from datetime import date, datetime, timedelta
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _

from communities.models import Community
from conference.constants import *
from networks.models import Network, ChapterInfo
from siteutils.models import Address

class ConferenceRegistration(models.Model):
    """Conference registration data"""
    
    user = models.ForeignKey(User, related_name="conference_registrations")
    chapter = models.ForeignKey(Network, related_name="conference_delegates", null=True)
    
    amountPaid = models.DecimalField(max_digits=6, decimal_places=2)
    roomSize = models.CharField(max_length=25)
    date = models.DateTimeField(default=datetime.now)
    headset = models.BooleanField(default=False)
    foodPrefs = models.CharField(max_length=10, choices=FOOD_CHOICES, default='none')
    cancelled = models.BooleanField(default=False)
    specialNeeds = models.TextField()
    emergName = models.CharField(max_length=255)
    emergPhone = models.CharField(max_length=50)
    prevConfs = models.SmallIntegerField(default=0)
    prevRetreats = models.SmallIntegerField(default=0)
    cellphone = models.CharField(max_length=50, blank=True, null=True)
    grouping = models.CharField(max_length=50, blank=True, null=True)
    
    txid = models.CharField(max_length=255)
    receiptNum = models.CharField(max_length=255)
    code = models.ForeignKey('ConferenceCode', related_name="registration", blank=True, null=True)
    type = models.CharField(max_length=50)
    africaFund = models.SmallIntegerField(blank=True, null=True)

    def cancel(self):
        self.cancelled = True
        self.chapter = None
        self.save()

        # remove from delegates group
        grp, created = Community.objects.get_or_create(slug='conference2011',
                                                       defaults={'invite_only': True,
                                                                 'name': 'National Conference 2011 - EWB delegates',
                                                                 'creator': self.user,
                                                                 'description': 'National Conference 2011 delegates (EWB members)',
                                                                 'mailchimp_name': 'National Conference 2011 members',
                                                                 'mailchimp_category': 'Conference'})

        grp2, created = Community.objects.get_or_create(slug='conference2011-external',
                                                        defaults={'invite_only': True,
                                                                  'name': 'National Conference 2011 - external delegates',
                                                                  'creator': self.user,
                                                                  'description': 'National Conference 2011 delegates (external)',
                                                                  'mailchimp_name': 'National Conference 2011 external',
                                                                  'mailchimp_category': 'Conference'})

        grp.remove_member(self.user)
        grp2.remove_member(self.user)
        
        # re-enable code
        if self.code and self.code.expired:
            self.code.expired = False
            self.code.save()
        
    def getRefundAmount(self):
        return self.amountPaid - 20

class InvalidCode(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)
    
class ConferenceCode(models.Model):
    """Registration code"""

    code = models.CharField(max_length=9)
    type = models.CharField(max_length=1, choices=CONF_CODES)
    number = models.IntegerField()
    
    generated = models.DateTimeField(default=datetime.now)
    
    # currently needs to be done manually, but fairly easy to write a UI for this
    expired = models.BooleanField(default=False)
    
    # not currently used, but may let us enforce code/chapter pairings
    chapter = models.ForeignKey(Network, related_name="conference_codes", verbose_name=_('chapter'), null=True)
    
    def __init__(self, *args, **kwargs):
        super(ConferenceCode, self).__init__(*args, **kwargs)
    
        # try/except to keep the admin page working
        try:
            self.type = kwargs['type']
            self.number = kwargs['number']
        
            self.expired = False

            m = hashlib.md5()
            m.update("%s%03d%s" % (self.type, self.number, CONF_HASH))
            self.code = "%s%03d%s" % (self.type, self.number, m.hexdigest()[:4])
        except:
            pass

    def getShortname(self):
        # CONF_CODES is a tuple so that it can be used as a choices= for 
        # the type field above... so we hack it here to make it act like a
        # dictionary
        for code in CONF_CODES:
            if code[0] == self.type.lower():
                return code[1]
        
        # should never get here, since the type field is restricted to CONF_CODES
        return "unknown"
    
    def isAvailable(self):
        if self.expired == True:
            return False
        
        try:
            ConferenceCode.objects.get(code=self.code, registration__cancelled=False)
        except ObjectDoesNotExist:
            return True
        except:
            pass

        return False

    @staticmethod
    def isValid(code):
        type = code[0]
        number = code[1:3]
        codehash = code[4:]
        
        m = hashlib.md5()
        m.update("%s%s%s" % (type, number, CONF_HASH))
        return codehash == m.hexdigest()[:4]

class AlumniConferenceCode(ConferenceCode):
    def getShortname(self):
        return 'alumni'
    
    def isAvailable(self):
        return True
    
class QuasiVIPCode(ConferenceCode):
    def getShortname(self):
        return 'discounted'
    
    def isAvailable(self):
        return True
        
class ConferenceRoom(models.Model):
    pass

SESSION_TYPES = (('keynote', "Keynote"),
                 ('speaker', "Speaker"),
                 ('panel', "Panel discussion"),
                 ('workshop', "Workshop"),
                 ('social', "Social time"),
                 ('networking', "Networking"),
                 ('other', "Other"))
                 
STREAMS = (('coalitions', 'Coalitions for Change'),
           ('prosperity', 'Unlocking African Prosperity'),
           ('rethinking', 'Rethinking Development'))
                 
class ConferenceSession(models.Model):
    name = models.CharField(max_length=255)
    room = models.ForeignKey(ConferenceRoom)
    day = models.DateField()
    time = models.TimeField()
    length = models.IntegerField(help_text="in minutes")
    sessiontype = models.CharField(max_length=50, choices=SESSION_TYPES)
    short_description = models.TextField(blank=True)
    long_description = models.TextField(blank=True)
    
    stream = models.CharField(max_length=50, choices=STREAMS)
    capacity = models.IntegerField()
    
    attendees = models.ManyToManyField(User, related_name="conference_sessions")
    maybes = models.ManyToManyField(User, related_name="conference_maybe")
    
    class Meta:
        ordering = ('day', 'time',)
        
    def dayverbose(self):
        if self.day == date(year=2011, month=1, day=13):
            return 'thurs'
        elif self.day == date(year=2011, month=1, day=14):
            return 'fri'
        elif self.day == date(year=2011, month=1, day=15):
            return 'sat'
        
        return ''
        
    def timeverbose(self):
        return "%02d%02d" % (self.time.hour, self.time.minute)
        
    def streamverbose(self):
        for sid, sname in STREAMS:
            if self.stream == sid:
                return sname
        
    def endtime(self):
        return self.time + timedelta(minutes=self.length)
        
    def user_is_attending(self, user):
        if user.is_authenticated():
            if user in self.attendees.all():
                return True
        return False
        
    def user_is_tentative(self, user):
        if user.is_authenticated():
            if user in self.maybes.all():
                return True
        return False

class ConferenceBlock(models.Model):
    user = models.ForeignKey(User)
    day = models.DateTimeField()
    length = models.IntegerField(help_text="in minutes")
    
