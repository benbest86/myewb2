"""myEWB mailchimp integration

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung <franciskung@ewb.ca>
"""

from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete

from account_extra.signals import signup, listsignup, deletion
from base_groups.models import BaseGroup, GroupMember
from mailchimp.models import ListEvent, GroupEvent, ProfileEvent
from profiles.models import MemberProfile

import settings

def list_subscribe(sender, user, **kwargs):
    ListEvent.objects.subscribe(user)

def list_unsubscribe(sender, user, **kwargs):
    ListEvent.objects.unsubscribe(user)

def group_join(sender, instance, created, **kwargs):
    membership = instance
    
    if created:
        user = membership.user
        group = membership.group
        groupname = membership.group.slug
        
        if group.mailchimp:
            GroupEvent.objects.join(user, groupname)

def group_leave(sender, membership, **kwargs):
    user = membership.user
    group = membership.group
    groupname = membership.group.slug
    
    if group.mailchimp:
        GroupEvent.objects.leave(user, groupname)

def user_update(sender, instance, created, **kwargs):
    user = instance
    
    if not created:
        ProfileEvent.objects.update(user)

def profile_update(sender, instance, created, **kwargs):
    profile = instance
    
    if not created:
        ProfileEvent.objects.update(profile.user2)

# only connect listeners if mailchimp is enabled
if settings.MAILCHIMP_KEY:
    signup.connect(list_subscribe)
    listsignup.connect(list_subscribe)
    deletion.connect(list_subscribe)
    post_save.connect(group_join, sender=GroupMember, dispatch_uid='mailchimp-group-join')
    pre_delete.connect(group_leave, sender=GroupMember, dispatch_uid='mailchimp-group-leave')
    post_save.connect(user_update, sender=User, dispatch_uid='mailchimp-user-update')
    post_save.connect(profile_update, sender=MemberProfile, dispatch_uid='mailchimp-profile-update')
