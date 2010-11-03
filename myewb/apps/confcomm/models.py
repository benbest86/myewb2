from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, UserManager, User

from django.utils.translation import ugettext_lazy as _

from profiles.models import MemberProfile
from networks.models import Network
from avatar.templatetags.avatar_tags import avatar_url
from conference.models import ConferenceRegistration

# Create your models here.

class ConferenceInterest(models.Model):
    """
    A topic of interest for members of conference.
    """
    name = models.CharField(_("Interest Name"), max_length=255)
    description = models.TextField(_("Interest Description"))

    def __unicode__(self):
        return self.name


class ConferenceProfile(models.Model):
    """
    An additional set of information tied to a MyEWB user specifically
    for the conference community website.
    """
    member_profile = models.OneToOneField(MemberProfile, unique=True, verbose_name=_('member profile this profile is linked to.'))
    registered = models.BooleanField(_('registered for conference 2011'), default=False)
    # additional personal information
    what_now = models.TextField(_("What you are doing now."), default="Edit me! What are you doing? Where are you living?")
    # additional information we want for conference.
    interests = models.ManyToManyField(ConferenceInterest, related_name='interested_users', verbose_name=_('List of interests.'), blank=True)
    conference_question = models.TextField(_("One question you want to answer at conference."), default="Add your question here!")
    conference_goals = models.TextField(_("Your goals for conference."), default="My goals for conference are...")
    active = models.BooleanField(default=False)

    @property
    def avatar_url(self):
        return avatar_url(self.member_profile.user, 200)

    @property
    def username(self):
        return self.member_profile.user.username

    @property
    def cohorts(self):
        if self.cohort_set.count() == 0:
            # return 5 random cohorts
            return Cohort.objects.all().order_by('?')[:5]
        cohorts = self.cohort_set.exclude(role__in=['p', 'j', 'f'])
        for c in self.cohort_set.filter(role__in=['p', 'j', 'f']):
            cohorts = cohorts | Cohort.objects.filter(role=c.role, year=c.year, chapter=None).order_by('year')
        return cohorts.distinct()

    def __unicode__(self):
        return '%s - %s' % (self.member_profile.name, (self.registered and 'registered' or 'not registered'))

CHAPTER_CHOICES = (
    ('carleton', 'Carleton',),
    ('concordia', 'Concordia',),
    ('dal', 'Dalhousie',),
    ('uoguelph', 'Guelph',),
    ('ulaval', 'Laval',),
    ('mcmaster', 'McMaster',),
    ('mcgill', 'McGill ',),
    ('mun', 'MUN',),
    ('polymtl', 'Polytechnique',),
    ('queensu', 'Queen\'s',),
    ('uregina', 'U of R',),
    ('ryerson', 'Ryerson',),
    ('sfu', 'SFU',),
    ('usherbrooke', 'Sherbrooke',),
    ('ubc', 'UBC',),
    ('unb', 'UNB',),
    ('ualberta', 'U of A',),
    ('ucalgary', 'U of C',),
    ('umanitoba', 'U of M',),
    ('utoronto', 'U of T',),
    ('uoit', 'UoIT',),
    ('uottawa', 'U of O',),
    ('usask', 'U of S',),
    ('uvic', 'UVic',),
    ('uwaterloo', 'Waterloo',),
    ('uwo', 'Western',),
    ('uwin', 'Windsor',),
    ('yorku', 'York',),
    ('vancouver', 'Vancouver',),
    ('calgary', 'Calgary',),
    ('edmonton', 'Edmonton',),
    ('saskatoon', 'Saskatoon',),
    ('winnipeg', 'Winnipeg',),
    ('grandriver', 'Grand River',),
    ('toronto', 'Toronto',),
    ('ottawa', 'Ottawa',),
    ('montreal', 'Montreal',),
    )
DICT_CHAPTER_CHOICES = dict(CHAPTER_CHOICES)
ROLE_CHOICES = (
        ('m', 'All Roles',),
        ('e', 'Executive',),
        ('p', 'President',),
        ('j', 'JF/Op 21',),
        ('f', 'ProF',),
        ('s', 'APS/OVS',),
        )

class Cohort(models.Model):
    """
    A definition of a Cohort of people we are looking at.
    """
    chapter = models.CharField(max_length=20, choices=CHAPTER_CHOICES, null=True, blank=True)
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default='m')
    year = models.PositiveIntegerField(default=2005)
    members = models.ManyToManyField(ConferenceProfile)

    def __unicode__(self):
        year_range = "%s/%s" % (str(self.year)[2:4], str(self.year+1)[2:4])
        if self.role == 'm':
            return '%s %s' % (DICT_CHAPTER_CHOICES[self.chapter], year_range)
        elif self.role == 'e':
            return '%s Executive %s' % (DICT_CHAPTER_CHOICES[self.chapter], year_range)
        elif self.role == 'p':
            return 'Chapter President %s' % (year_range)
        elif self.role == 'j':
            r = (self.year < 2006) and 'Op 21' or 'JF'
            return '%s %d' % (r, self.year)
        elif self.role == 's':
            r = (self.year < 2009) and 'OVS' or 'APS'
            return '%s %d' % (r, self.year)
        elif self.role == 'f':
            return 'ProF %d' % self.year

    @property
    def display(self):
        return str(self)

    @property
    def relevant_properties(self):
        if self.role in ['m', 'e', 'p']:
            return ['chapter', 'role', 'year']
        else:
            return ['role', 'year']
cohort_ct = ContentType.objects.get(app_label='confcomm', model='cohort')
kohort_kings,created = Permission.objects.get_or_create(name='Kohort King', codename='kohort_king', content_type=cohort_ct)



CANADA_ROLE_CHOICES = (
        ('m', 'Member',),
        ('e', 'Executive',),
        ('p', 'President',),
        )
class CanadaCohort(models.Model):
    """
    A definition of a Cohort of people that we are looking at.
    """
    chapter = models.CharField(max_length=40,choices=CHAPTER_CHOICES)
    role = models.CharField(max_length=1, choices=CANADA_ROLE_CHOICES)
    year = models.PositiveIntegerField()
    members = models.ManyToManyField(ConferenceProfile)

AFRICA_ROLE_CHOICES = (
        ('j', 'JF/Op 21',),
        ('p', 'ProF',),
        ('s', 'APS/OVS',),
        )
AFRICA_COUNTRY_CHOICES = (
        ('bf', 'Burkina Faso',),
        ('gh', 'Ghana',),
        ('mw', 'Malawi',),
        ('zm', 'Zambia',),
        ('ml', 'Mali',),
        ('ph', 'Philippines',),
        ('tz', 'Tanzania',),
        ('cm', 'Cameroon',),
        ('kh', 'Cambodia',),
        )
class AfricaCohort(models.Model):
    """
    A definition of a Cohort in terms of Africa.
    """
    country = models.CharField(_('Country'), max_length=2, choices=AFRICA_COUNTRY_CHOICES) # Ghana, Burkina, etc.
    role = models.CharField(_('Role'), max_length=1, choices=AFRICA_ROLE_CHOICES) # APS/OVS, JF/OP21, ProF
    year = models.PositiveIntegerField()
    members = models.ManyToManyField(ConferenceProfile)

class ConferenceInvitation(models.Model):
    """
    Keep track of invitations that are sent and clicked on.
    """
    sender = models.ForeignKey(ConferenceProfile, related_name='sent_conference_invitations')
    receiver = models.ForeignKey(ConferenceProfile, related_name='received_conference_invitations')
    code = models.CharField(max_length=12)
    activated = models.BooleanField()
    sent = models.DateTimeField(auto_now_add=True)

    def save(self, force_insert=False, force_update=False):
        if not self.code:
            code = UserManager().make_random_password(12)
            while ConferenceInvitation.objects.filter(code=code).count() > 0:
                code = UserManager().make_random_password(12)
            self.code = code
        return super(ConferenceInvitation, self).save(force_insert, force_update)

class RegistrationHit(models.Model):
    """
    Keep track of how many people move to the registration screen from this system.
    """
    user = models.ForeignKey(User, null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    ip_address = models.IPAddressField(null=True, blank=True)

def update_registered_status(sender, **kwargs):
    try:
        cp = ConferenceProfile.objects.get(member_profile__user=instance.user)
        if instance.user.conference_registrations.filter(cancelled=False).count() > 0:
            if not cp.registered:
                cp.registered = True
                cp.save()
        else:
            if cp.registered:
                cp.registered = False
                cp.save()
    except:
        pass
post_save.connect(update_registered_status, sender=ConferenceRegistration)

def create_conference_profiles(do=False):
    all_mps = MemberProfile.objects.exclude(Q(name__isnull=True) | Q(user__is_active=False) | Q(user__is_bulk=True))
    created = 0
    for mp in all_mps:
        if not ConferenceProfile.objects.filter(member_profile=mp).count():
            registered = mp.user.conference_registrations.filter(cancelled=False).count() > 0
            cp = ConferenceProfile(member_profile=mp, registered=registered)
            if do:
                print 'Saving ', cp
                cp.save()
            else:
                print 'Not saving - pass True to save.', cp
            created += 1
        print created, ' ConferenceProfiles created.'
