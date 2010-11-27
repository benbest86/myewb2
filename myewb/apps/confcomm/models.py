from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, UserManager, User

from django.utils.translation import ugettext_lazy as _

from profiles.models import MemberProfile
from networks.models import Network
from communities.models import ExecList
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
    what_now = models.TextField(_("What you are doing now."),)
    # additional information we want for conference.
    interests = models.ManyToManyField(ConferenceInterest, related_name='interested_users', verbose_name=_('List of interests.'), blank=True)
    text_interests = models.TextField(_('Your current interests'),default="",)
    conference_question = models.TextField(_("One question you want to answer at conference."),)
    conference_goals = models.TextField(_("Your goals for conference."),)
    active = models.BooleanField(default=False)

    @property
    def avatar_url(self):
        return avatar_url(self.member_profile.user, 200)

    @property
    def username(self):
        return self.member_profile.user.username

    @property
    def cohorts(self):
        cohorts = self.cohort_set.exclude(role__in=['p', 'j', 'f'])
        for c in self.cohort_set.filter(role__in=['p', 'j', 'f']):
            cohorts = cohorts | Cohort.objects.filter(role=c.role, year=c.year, chapter=None).order_by('year')
        return cohorts.distinct()
    @property
    def blurb(self):
        if self.registered:
            length = 45
        else:
            length = 15
        blurb = ' '.join(self.conference_goals[:length].split()[:-1])
        return blurb

    def __unicode__(self):
        return '%s - %s' % (self.member_profile.name, (self.registered and 'registered' or 'not registered'))

    def add_to_default_cohorts(self):
        """
        Add a conference profile to its default cohorts based on chapter
        status.
        """
        #XXX this is a bad hack that probably should go somewhere
        # else. In fact this whole thing should probably be a manager
        # function :)
        chapter = self.member_profile.get_chapter()
        if chapter is not None:
            print 'chapter is there!'
            Cohort.objects.get(chapter=chapter.slug, role='m', year=2010).members.add(self)
            execlist = ExecList.objects.get(parent=chapter)
            if execlist.members.filter(user__id=self.member_profile.user.id).count():
                Cohort.objects.get(chapter=chapter.slug, role='e', year=2010).members.add(self)
        if self.member_profile.name is None:
            mp = self.member_profile
            if mp.user.visible_name():
                mp.name = mp.user.visible_name()
                mp.save()


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
    role = models.CharField(max_length=1, choices=ROLE_CHOICES)
    year = models.PositiveIntegerField()
    members = models.ManyToManyField(ConferenceProfile)

    def __unicode__(self):
        s = []
        if self.chapter:
            s.append(DICT_CHAPTER_CHOICES[self.chapter])
        if self.role == 'm':
            pass
        elif self.role == 'e':
            s.append('Executive')
        elif self.role == 'p':
            s.append('Chapter President')
        elif self.role == 'j':
            if self.year is None or self.year >= 2006:
                s.append('JF')
            else:
                s.append('Op 21')

        elif self.role == 's':
            if self.year is None or self.year >= 2009:
                s.append('APS')
            else:
                s.append('OVS')
        elif self.role == 'f':
            s.append('ProF')
        if self.year:
            # if a chapter role, use YY/YY format for school year
            if self.role in ['m', 'e', 'p',]:
                s.append("%s/%s" % (str(self.year)[2:4], str(self.year+1)[2:4]))
            # if an africa role, use YYYY format
            else:
                s.append(str(self.year))
        return " ".join(s)

    @property
    def display(self):
        return str(self)

    @property
    def relevant_properties(self):
        if self.role in ['m', 'e', 'p']:
            return ['chapter', 'role', 'year']
        else:
            return ['role', 'year']
try:
    cohort_ct = ContentType.objects.get(app_label='confcomm', model='cohort')
    kohort_kings,created = Permission.objects.get_or_create(name='Kohort King', codename='kohort_king', content_type=cohort_ct)
except:
    pass



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

def update_registered_status(sender, instance, **kwargs):
    cp, created = ConferenceProfile.objects.get_or_create(member_profile=instance.user.get_profile())
    cp.registered = not instance.cancelled
    cp.save()
post_save.connect(update_registered_status, sender=ConferenceRegistration)

def create_conference_profile_on_save(sender, **kwargs):
    try:
        if isinstance(instance, User):
            user = instance
            member_profile = instance.get_profile()
        elif isinstance(instance, MemberProfile):
            user = instance.user
            member_profile = instance
        else:
            return
        if user.is_active and not user.is_bulk and member_profile.name:
            cp, created = ConferenceProfile.objects.get_or_create(member_profile=member_profile)
            if created:
                cp.add_to_default_cohorts()
                if user.conference_registrations.filter(cancelled=False).count():
                    cp.registered = True
                    cp.save()
    except:
        pass
post_save.connect(create_conference_profile_on_save, sender=MemberProfile)
post_save.connect(create_conference_profile_on_save, sender=User)

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
