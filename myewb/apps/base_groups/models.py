import datetime

from django.core.urlresolvers import reverse
from django.contrib.auth.models import  User
from django.utils.translation import ugettext_lazy as _
from django.db import models

from groups.base import Group

class BaseGroup(Group):
    """Base group (from which networks, communities, projects, etc. derive).
    
    Not intended to be instantiated by itself.
    """
    
    member_users = models.ManyToManyField(User, through="GroupMember", verbose_name=_('members'))
    # TODO: parent groups
	
	# private means only members can see the group
    private = models.BooleanField(_('private'), default=False)
	
    def user_is_member(self, user):
        if GroupMember.objects.filter(group=self, user=user).count() > 0: # @@@ is there a better way?
            return True
        else:
            return False
            
    def user_is_admin(self, user):
        member_objects = GroupMember.objects.filter(group=self, user=user)
        if member_objects.count() > 0:
            member = member_objects[0]
            return member.is_admin
        else:
            return False
	
	# TODO:
	# mailing list
	# list of members (NOT CSV)
	
class GroupMember(models.Model):
    group = models.ForeignKey(BaseGroup, related_name="members", verbose_name=_('group'))
    user = models.ForeignKey(User, related_name="member_groups", verbose_name=_('user'))
    is_admin = models.BooleanField(_('admin'), default=False)
    admin_title = models.CharField(_('admin title'), max_length=500, null=True, blank=True)
    joined = models.DateTimeField(_('joined'), default=datetime.datetime.now)

    # away = models.BooleanField(_('away'), default=False)
    # away_message = models.CharField(_('away_message'), max_length=500)
    # away_since = models.DateTimeField(_('away since'), default=datetime.now)

class GroupLocation(models.Model):
    group = models.ForeignKey(BaseGroup, related_name="locations", verbose_name=_('group'))
    place = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)