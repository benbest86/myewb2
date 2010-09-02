"""myEWB mailchimp integration

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung <franciskung@ewb.ca>
"""

from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, pre_delete
from emailconfirmation.signals import email_confirmed

from account_extra.signals import listsignup, deletion
from base_groups.models import BaseGroup, GroupMember
from mailchimp.models import ListEvent, GroupEvent, ProfileEvent
from profiles.models import MemberProfile

import settings

# expecting a user instance
def list_unsubscribe(sender, user, **kwargs):
    ListEvent.objects.unsubscribe(user)

def group_join(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        group = instance.group
        
        if group.mailchimp_name:
            GroupEvent.objects.join(user, group)

def group_leave(sender, instance, **kwargs):
    user = instance.user
    group = instance.group
    
    if group.mailchimp_name or group.mailchimp_past_name:
        GroupEvent.objects.leave(user, group)

def user_update(sender, instance, created=None, **kwargs):
    user = instance
    
    if not user.email:
        return
    
    # pre-save only (created is None);
    if created is None:
        # instance already exists - we're updating an existing user...
        if user.pk:
            
            original_user = User.objects.get(id=instance.pk)

            # nomail flag is set?  just unsub them and bail.
            #if user.nomail:
            #    if not original_user.nomail:
            #        return list_unsubscribe(sender, user, kwargs)
            #    else:
            #        return
            # the above is commented out since mailchimp callbacks were triggering
            # this... but since we never set nomail ourselves, it should be fine
            # to not handle this case...
            if user.nomail:
                return

            # nomail flag just unset?  just subscribe them...
            if original_user.nomail and not user.nomail:
                return ProfileEvent.objects.update(user)

            # check for an email address change
            original_email = None
            if original_user.email != user.email:
                original_email = original_user.email
                
            # TODO: do some checking so we only update on sync'ed fields 
    
            ProfileEvent.objects.update(user, email=original_email)

    # otherwise, this is actually a post-save
    # (and the only post-save we handle is new user creation.  updates to
    #  existing users are handled above)
    elif created == True:
        ProfileEvent.objects.update(user)
    
def profile_update(sender, instance, **kwargs):
    return user_update(sender, instance.user2, kwargs)

# only connect listeners if mailchimp is enabled
if settings.MAILCHIMP_KEY:
    deletion.connect(list_unsubscribe)
    post_save.connect(group_join, sender=GroupMember, dispatch_uid='mailchimp-group-join')
    pre_delete.connect(group_leave, sender=GroupMember, dispatch_uid='mailchimp-group-leave')
    pre_save.connect(user_update, sender=User, dispatch_uid='mailchimp-user-preupdate')
    post_save.connect(user_update, sender=User, dispatch_uid='mailchimp-user-postupdate')
    pre_save.connect(profile_update, sender=MemberProfile, dispatch_uid='mailchimp-profile-update')
