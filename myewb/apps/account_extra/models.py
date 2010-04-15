from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from emailconfirmation.models import EmailAddress
from manager_extras.models import ExtraUserManager
from avatar.models import Avatar
from account_extra import signals

def clean_up_email_addresses(sender, instance, created, **kwargs):
    """
    Cleans up unverified emails with the same email and deletes any users who
    have no remaining emails.
    """
    if instance.verified:
        others = EmailAddress.objects.filter(email__iexact=instance.email, verified=False)
        for o in others:
            u = o.user
            o.delete()
            if u.emailaddress_set.count() == 0:
                u.delete()
post_save.connect(clean_up_email_addresses, sender=EmailAddress)

# some duck punches to the User class and extras Manager

# add an is_bulk boolean directly to the User model
User.add_to_class('is_bulk', models.BooleanField(default=False))

def create_bulk_user_method(self, email):
    # ensure email is not already in use
    emailaddress = EmailAddress.objects.filter(email=email, verified=True)  # shoudl I remove the verified=True ?
    if emailaddress.count() > 0:
        return emailaddress[0].user
    
    # create random username
    username = User.objects.make_random_password()
    while User.objects.filter(username=username).count() > 0:   # ensure uniqueness
        username = User.objects.make_random_password()
    
    # create the user
    new_user = self.create_user(username=username, email=email)
    new_user.is_bulk = True
    new_user.save()
    
    # and the EmailAddress object too (should this be a User.postsave instead?)
    EmailAddress.objects.add_email(new_user, email)
    
    # and finish up
    signals.listsignup.send(sender=new_user, user=new_user)
    return new_user
ExtraUserManager.create_bulk_user = create_bulk_user_method

# add a delete function directly to the User model; doesn't delete the database
# object, but deletes personal info, unsub's from groups, and marks user
# as inactive
def softdelete(self, *args, **kwargs):
    # remove from all groups
    for group in self.basegroup_set.all():
        group.remove_member(self)
        
    # delete profile picture
    avatars = Avatar.objects.filter(user=self)
    for avatar in avatars:
        avatar.delete()
    
    self.get_profile().delete()
    self.email = ""
    for email in self.emailaddress_set.all():
        email.delete()
    # do we need to do this (ie for privacy law? FIXME )
    #self.first_name = "deleted"
    #self.last_name = "user"
    self.is_active = False
    self.save()
    signals.deletion.send(sender=self, user=self)
    
User.softdelete = softdelete
