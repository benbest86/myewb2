from django.db import models

from django.utils.translation import ugettext_lazy as _

from profiles.models import MemberProfile

# Create your models here.

class ConferenceProfile(models.Model):
    """
    An additional set of information tied to a MyEWB user specifically
    for the conference community website.
    """
    member_profile = models.ForeignKey(MemberProfile, unique=True, verbose_name=_('member profile this profile is linked to.'))
    # additional information we want for conference.
