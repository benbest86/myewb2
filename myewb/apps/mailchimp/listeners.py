"""myEWB mailchimp integration

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung <franciskung@ewb.ca>
"""

from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from emailconfirmation.signals import email_confirmed

from account_extra.signals import listsignup, deletion
from base_groups.models import BaseGroup, GroupMember
from mailchimp.models import ListEvent, GroupEvent, ProfileEvent
from profiles.models import MemberProfile

import settings

# from a bulk-subscribe (is passed a user)
def list_subscribe(sender, user, **kwargs):
    ListEvent.objects.subscribe(user)
    
# from a web sign-up, sent on email confirmation (is passed a EmailAddress)
def list_subscribe2(sender, email_address, **kwargs):
    ListEvent.objects.subscribe(email_address.user)

# expecting a user instance
def list_unsubscribe(sender, user, **kwargs):
    ListEvent.objects.unsubscribe(user)

def group_join(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        group = instance.group
        
        if group.mailchimp:
            GroupEvent.objects.join(user, group)

def group_leave(sender, instance, **kwargs):
    user = instance.user
    group = instance.group
    
    if group.mailchimp:
        GroupEvent.objects.leave(user, group)

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
    listsignup.connect(list_subscribe)
    email_confirmed.connect(list_subscribe2)
    deletion.connect(list_unsubscribe)
    post_save.connect(group_join, sender=GroupMember, dispatch_uid='mailchimp-group-join')
    pre_delete.connect(group_leave, sender=GroupMember, dispatch_uid='mailchimp-group-leave')
    post_save.connect(user_update, sender=User, dispatch_uid='mailchimp-user-update')
    post_save.connect(profile_update, sender=MemberProfile, dispatch_uid='mailchimp-profile-update')
