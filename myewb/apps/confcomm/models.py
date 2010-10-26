from django.db import models

from django.utils.translation import ugettext_lazy as _

from profiles.models import MemberProfile

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
    # additional information we want for conference.
    interests = models.ManyToManyField(ConferenceInterest, related_name='interested_users', verbose_name=_('List of interests.'), blank=True)
    conference_question = models.TextField(_("One question you want to answer at conference."))
    conference_goals = models.TextField(_("Your goals for conference."))
