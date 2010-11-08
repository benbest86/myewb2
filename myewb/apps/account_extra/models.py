from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from emailconfirmation.models import EmailAddress
from manager_extras.models import ExtraUserManager
from avatar.models import Avatar
from account_extra import signals
from networks.models import Network
from communities.models import Community
from base_groups.helpers import get_counts, get_recent_counts
from base_groups.models import BaseGroup

import settings

def clean_up_email_addresses(sender, instance, created, **kwargs):
    """
    Cleans up unverified emails with the same email and deletes any users who
    have no remaining emails. Sets the verified user to not bulk.
    """
    if instance.verified:
        others = EmailAddress.objects.filter(email__iexact=instance.email, verified=False)
        for o in others:
            u = o.user
            o.delete()
            if u.emailaddress_set.count() == 0:
                try:
                    u.delete()
                except:
                    # sometimes the db can generate a ForeignKey error on the delete...
                    # so do this as a fallback
                    u.is_active = False
                    u.save()
        u = instance.user
        if u.is_bulk:
            u.is_bulk = False
            u.save()
post_save.connect(clean_up_email_addresses, sender=EmailAddress)

# some duck punches to the User class and extras Manager

# add an is_bulk boolean directly to the User model
User.add_to_class('is_bulk', models.BooleanField(default=False))

# add a no-mail setting directly to the User model too
User.add_to_class('nomail', models.BooleanField(default=False))
User.add_to_class('bouncing', models.BooleanField(default=False))

def create_bulk_user_method(self, email):
    # ensure email is not already in use
    emailaddress = EmailAddress.objects.filter(email=email, verified=True)  # shoudl I remove the verified=True ?
    if emailaddress.count() > 0:
        return emailaddress[0].user
    
    emailaddress2 = User.objects.filter(email=email)  # hmm.. would happen if a bulk user already exists, i think?
    if emailaddress2.count() > 0:
        return emailaddress2[0]

    # create random username
    username = User.objects.make_random_password()
    while User.objects.filter(username=username).count() > 0:   # ensure uniqueness
        username = User.objects.make_random_password()
    
    # create the user
    new_user = self.create_user(username=username, email=email)
    new_user.is_bulk = True
    new_user.save()
    
    # and the EmailAddress object too (should this be a User.postsave instead?)
    # (do not use EmailAddress.objects.add_email since that will generate a verification email)
    try:
        EmailAddress.objects.create(user=new_user, email=email)
    except:
        pass
    
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
    old_email = self.email
    self.email = ""
    for email in self.emailaddress_set.all():
        email.delete()
    # do we need to do this (ie for privacy law? FIXME )
    #self.first_name = "deleted"
    #self.last_name = "user"
    self.is_active = False
    self.save()
    signals.deletion.send(sender=self, user=self, email=old_email)
    
User.softdelete = softdelete

def get_networks(self):
    return Network.objects.filter(member_users=self, is_active=True).order_by('name')
User.get_networks = get_networks

def get_groups(self):
    # un-hardcode the LogisticalGroup bit.  shoudl probably subclass BaseGroup to VisibleGroup first.
    grps = BaseGroup.objects.filter(member_users=self, is_active=True).exclude(model="LogisticalGroup")
    return get_recent_counts(grps, BaseGroup).order_by('-recent_topic_count')
User.get_groups = get_groups

def get_communities(self):
    return Community.objects.filter(member_users=self, is_active=True).order_by('name')
User.get_communities = get_communities

# override user password management so that I can integrate with Google Apps
check_password2 = User.check_password
set_password2 = User.set_password
User.add_to_class('google_username', models.CharField(null=True, blank=True, max_length=255))
User.add_to_class('google_sync', models.BooleanField(default=False))

def set_google_password(username, password):
    if settings.GOOGLE_APPS and username:
        try:
            # update google account
            import gdata.apps.service
            service = gdata.apps.service.AppsService(email=settings.GOOGLE_ADMIN,
                                                     domain=settings.GOOGLE_DOMAIN,
                                                     password=settings.GOOGLE_PASSWORD)
            service.ProgrammaticLogin()
        
            user = service.RetrieveUser(username)
            user.login.password = password
            service.UpdateUser(username, user)
        except:
            return False
        
        try:
            # update legacy ldap accounts
            import ldap
            from ldap import modlist as ml
            import hashlib, base64
        
            myewbIdField = 'uid'
            basedn = 'ou=people,dc=ewb,dc=ca'
            scope = ldap.SCOPE_ONELEVEL
            
            l = ldap.initialize(settings.LDAP_HOST)
            l.bind_s(settings.LDAP_BIND_DN, settings.LDAP_BIND_PW)
            
            name = "%s=%s,%s" % (myewbIdField, username, basedn)
            h = hashlib.sha1(password)
            result = l.modify_s(name, [(ldap.MOD_REPLACE,
                                        'userPassword',
                                        "{SHA}" + base64.encodestring(h.digest()).strip())])
        except:
            pass
    return True

def check_password(self, raw_password):
    result = check_password2(self, raw_password)
    if result and not self.google_sync:
        sync = set_google_password(self.google_username, raw_password)
        if sync:
            self.google_sync = True
            self.save()
    return result

def set_password(self, raw_password):
    result = set_google_password(self.google_username, raw_password)
    if result:
        self.google_sync = True
        set_password2(self, raw_password)
    return result

User.check_password = check_password
User.set_password = set_password
