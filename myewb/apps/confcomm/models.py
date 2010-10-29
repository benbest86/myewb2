from django.db import models

from django.utils.translation import ugettext_lazy as _

from profiles.models import MemberProfile
from networks.models import Network
from avatar.templatetags.avatar_tags import avatar_url

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
    member_profile = models.ForeignKey(MemberProfile, unique=True, verbose_name=_('member profile this profile is linked to.'))
    registered = models.BooleanField(_('registered for conference 2011'), default=False)
    # additional personal information
    what_now = models.TextField(_("What you are doing now."), default="Edit me! What are you doing? Where are you living?")
    # additional information we want for conference.
    interests = models.ManyToManyField(ConferenceInterest, related_name='interested_users', verbose_name=_('List of interests.'), blank=True)
    conference_question = models.TextField(_("One question you want to answer at conference."), default="Add your question here!")
    conference_goals = models.TextField(_("Your goals for conference."), default="My goals for conference are...")

    @property
    def avatar_url(self):
        return avatar_url(self.member_profile.user, 160)

    @property
    def username(self):
        return self.member_profile.user.username

CHAPTER_CHOICES = []
chapterlist = Network.objects.filter(chapter_info__isnull=False, is_active=True).order_by('name')
for chapter in chapterlist:
    CHAPTER_CHOICES.append((chapter.slug, chapter.chapter_info.chapter_name))

CANADA_ROLE_CHOICES = (
        ('e', 'Executive',),
        ('p', 'President',),
        ('m', 'Member',),
        )
class CanadaCohort(models.Model):
    """
    A definition of a Cohort of people that we are looking at.
    """
    chapter = models.CharField(max_length=40,choices=CHAPTER_CHOICES)
    role = models.CharField(max_length=1, choices=CANADA_ROLE_CHOICES)
    year = models.PositiveIntegerField()
    members = models.ManyToManyField(MemberProfile)

AFRICA_ROLE_CHOICES = (
        ('j', 'Junior Fellow/Operation 21',),
        ('s', 'African Programs Staff/Overseas Volunteer Staff',),
        ('p', 'Professional Fellow',),
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
    members = models.ManyToManyField(MemberProfile)

class ConferenceInvitation(models.Model):
    """
    Keep track of invitations that are sent and clicked on.
    """
    sender = models.ForeignKey(MemberProfile, related_name='sent_conference_invitations')
    receiver = models.ForeignKey(MemberProfile, related_name='received_conference_invitations')
    code = models.CharField(max_length=12)
    activated = models.BooleanField()
