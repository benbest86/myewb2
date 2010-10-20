"""myEWB base groups models declarations

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Last modified on 2009-07-29
@author Joshua Gorner, Benjamin Best
"""

import datetime
import re
import unicodedata

from django.core.urlresolvers import reverse
from django.contrib.auth.models import  User
from django.utils.translation import ugettext_lazy as _
from django.db import models, connection
from django.db.models.signals import post_save, pre_delete
from django.conf import settings

from mailer import send_mail
from emailconfirmation.models import EmailAddress

from siteutils.helpers import get_email_user
from manager_extras.models import ExtraUserManager
from groups.base import Group
#from whiteboard.models import Whiteboard
from messages.models import Message

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

class BaseGroup(Group):
    """Base group (from which networks, communities, projects, etc. derive).
    
    Not intended to be instantiated by itself.
    """
    
    model = models.CharField(_('group model'), max_length=500, null=True, blank=True)
    parent = models.ForeignKey('self', related_name="children",
                               verbose_name=_('parent'), null=True, blank=True)
    
    member_users = models.ManyToManyField(User, through="GroupMember", verbose_name=_('members'))
    
    # if true, members can only join if invited
    invite_only = models.BooleanField(_('invite only'), default=False)
    
    VISIBILITY_CHOICES = (
        ('E', _("everyone")),
        ('P', _("group members and members of parent network only")),
        ('M', _("group members only"))
    )
    visibility = models.CharField(_('visibility'), max_length=1, choices=VISIBILITY_CHOICES, default='E')
    
    whiteboard = models.ForeignKey('whiteboard.Whiteboard', related_name="group", verbose_name=_('whiteboard'), null=True)
    
    from_name = models.CharField(_('From name'), max_length=255, blank=True,
                                 help_text='"From" name when sending emails to group members')
    from_email = models.CharField(_('From email'), max_length=255, blank=True,
                                  help_text='"From" email address when sending emails to group members')
    
    welcome_email = models.TextField(_('Welcome email'), blank=True, null=True,
                                     help_text='Welcome email to send when someone joins or is added to this group (leave blank for none)')
    
    secret_key = models.CharField(max_length=255, blank=True, null=True, default=None, editable=False)
    is_project = models.NullBooleanField(blank=True, null=True, editable=False) # to save info during migration. not really used.
    is_active = models.BooleanField(_("Is active? (false means deleted group"),
                                    default=True,
                                    editable=False)

    def is_visible(self, user):
        visible = False
        
        # public groups are always visible
        if self.visibility == 'E' or self.slug == 'ewb':
            visible = True
            
        elif user.is_authenticated():
            # site-wide group admins can see everything
            if user.has_module_perms("base_groups"):
                return True
                
            # admins of the parent group are automatically admins here
            if self.parent and self.parent.user_is_admin(user):
                return True
            
            # members of the group can see the group...
            member_list = self.members.filter(user=user)
            if member_list.count() > 0:
                visible = True
                
            # and the last option, members of the parent group can see this one
            elif self.visibility == 'P':
                parent_member_list = self.parent.members.filter(user=user)
                if parent_member_list.count() > 0:
                    visible = True
                    
        return visible
    
    # setting admin_override = True means that admins will be considered group members
    def user_is_member(self, user, admin_override = False):
        if admin_override and user.has_module_perms("base_groups"):
            return True
        if self.slug == 'ewb':
            return True
        return user.is_authenticated() and (self.members.filter(user=user).count() > 0)
        
    def user_is_member_or_pending(self, user):
        return user.is_authenticated() and ((self.members.filter(user=user).count() > 0) or self.pending_members.filter(user=user).count() > 0)

    def user_is_pending_member(self, user):
        return user.is_authenticated() and self.pending_members.filter(user=user).count() > 0
    
    # setting admin_override = False means that site admins and parent group admins 
    # are not automatically admins of the group (need explicit permission)
    def user_is_admin(self, user, admin_override = True):
        if user.is_authenticated():
            # site-wide group admins are admins here...
            if user.has_module_perms("base_groups") and admin_override:
                return True
                
            # admins of the parent group are admins here...
            if self.parent and self.parent.user_is_admin(user) and admin_override:
                return True
            
            # and check for regular admins
            if self.members.filter(user=user, is_admin=True).count() > 0:
                return True
        
        return False
    
    # subclasses should override this...
    def can_bulk_add(self, user):
        return False

    def get_absolute_url(self):
        return reverse('group_detail', kwargs={'group_slug': self.slug})

    def get_member_emails(self):
        members_with_emails = self.members.all().select_related(depth=1)
        return [member.user.email for member in members_with_emails if member.user.email and not member.user.nomail]

    def add_member(self, user):
        """
        Adds a member to a group.
        Retained for backwards compatibility with request_status days.
        Wait, should I not be actively using this?  Because it's a very useful function =)
        """
        member = GroupMember.objects.filter(user=user, group=self)
        if member.count() > 0:
            return member[0]
        else:
            return GroupMember.objects.create(user=user, group=self)
    
    def add_email(self, email):
        """
        Adds an email address to the group, creating the new bulk user if needed
        """
        email_user = get_email_user(email)
        if email_user is None:
            email_user = User.extras.create_bulk_user(email)
        
        self.add_member(email_user)
    
    def remove_member(self, user):
        member = GroupMember.objects.filter(user=user, group=self)
        for m in member:
            m.delete()
            
    def send_mail_to_members(self, subject, htmlBody,
                             fail_silently=False, sender=None,
                             context={}):
        """
        Creates and sends an email to all members of a network using Django's
        EmailMessage.
        Takes in a a subject and a message and an optional fail_silently flag.
        Automatically sets:
        from_email: the sender param, or group_name <group_slug@ewb.ca>
                (note, NO validation is done on "sender" - it is assumed clean!!)
        to: list-group_slug@ewb.ca
        bcc: list of member emails
        """
        
        if sender == None:
            sender = '%s <%s@ewb.ca>' % (self.name, self.slug)
            
        lang = 'en'
        try:
            # is there a cleaner way to do this???!!!
            if self.network.chapter_info.francophone:
                lang = 'fr'
        except:
            pass

        send_mail(subject=subject,
                  txtMessage=None,
                  htmlMessage=htmlBody,
                  fromemail=sender,
                  recipients=self.get_member_emails(),
                  context=context,
                  shortname=self.slug,
                  lang=lang)
    
    def save(self, force_insert=False, force_update=False):
        # if we are updating a group, don't change the slug (for consistency)
        created = False
        if not self.id:
            created = True
            slug = self.slug
            slug = slug.replace(' ', '-')
            
            # translates accents into their regular-character equivalent
            # (http://snippets.dzone.com/posts/show/5499)
            slug = unicodedata.normalize('NFKD', unicode(slug)).encode('ASCII', 'ignore')
            
            #(?P<group_slug>[-\w]+) This is the
            # regex definition of a slug so if we don't match on this we 
            # should remove illegal characters.
            match = re.match(r'[-\w]+', slug)
            if match is None or not match.group(0) == slug:
                slug = re.sub(r'[^-\w]+', '', slug)
            
            # check if slug is in use; increment until we find a good one.
            # (is there anything better than numerical incrementing?)
            temp_groups = BaseGroup.objects.filter(slug__contains=slug)
            #temp_groups = BaseGroup.objects.filter(slug__contains=slug, model=self.model)

            if (temp_groups.count() != 0):
                slugs = [n.slug for n in temp_groups]
                old_slug = slug
                i = 0
                while slug in slugs:
                    i = i + 1
                    slug = old_slug + "%d" % (i, )
                
            self.slug = slug
            
        # also give from_name and from_email reasonable defaults if needed
        if not self.from_name:
            self.from_name = "myEWB notices"
        if not self.from_email:
            self.from_email = "notices@my.ewb.ca"
        
        super(BaseGroup, self).save(force_insert=force_insert, force_update=force_update)
        post_save.send(sender=BaseGroup, instance=self, created=created)

    def delete(self):
        for m in self.member_users.all():
            self.remove_member(m)

        self.is_active = False
        self.save()
        #super(BaseGroup, self).delete()

    def get_url_kwargs(self):
        return {'group_slug': self.slug}
        
    def get_visible_children(self, user):
        if not user.is_authenticated():
            return self.children.filter(visibility='E', is_active=True)
        elif user.has_module_perms("base_groups") | self.user_is_admin(user):
            return self.children.filter(is_active=True)
        else:
            children = self.children.filter(visibility='E') | self.children.filter(member_users=user)
            if self.user_is_member(user):
                children = children | self.children.filter(visibility='P')
            return children.filter(is_active=True).distinct()
            #return children
            
    def get_accepted_members(self):
        """
        Accepted members are members that are not bulk (i.e. mailing list)
        users. They have a profile on the site and have signed up for MyEWB.
        """
        # is_bulk is set to True for bulk members
        return self.members.filter(user__is_bulk=False)

    def num_pending_members(self):
        return self.pending_members.all().count()
        
    def workspace_view_perms(self, user):
        return self.user_is_member(user, admin_override=True)
        
    def workspace_edit_perms(self, user):
        return self.user_is_admin(user)
    
"""
A hidden, private group that does not show up in any listing except for admins.
Used for logistical purposes, etc.
"""
class LogisticalGroup(BaseGroup):
    """
    visibility = models.CharField(_('visibility'), max_length=1,
                                  choices=BaseGroup.VISIBILITY_CHOICES,
                                  default='M', editable=False)
    invite_only = models.BooleanField(_('invite only'), default=True,
                                      editable=False)
    parent = models.ForeignKey('self', related_name="children",
                               verbose_name=_('parent'), null=True, blank=True,
                              editable=False)
    """

    """
    visibility = 'M'
    invite_only = True
    parent = None
    """

    def save(self, force_insert=False, force_update=False):
        self.model = "LogisticalGroup"
        self.visibility = 'M'
        self.invite_only = True
        self.parent = None
        return super(LogisticalGroup, self).save(force_insert, force_update)

class BaseGroupMember(models.Model):
    is_admin = models.BooleanField(_('Exec / Leader'), default=False)
    admin_title = models.CharField(_('Title'), max_length=500, null=True, blank=True)
    admin_order = models.IntegerField(_('admin order (smallest numbers come first)'), default=999, blank=True, null=True)
    joined = models.DateTimeField(_('joined'), default=datetime.datetime.now)
    imported = models.BooleanField(default=False, editable=False)
    
    class Meta:
        abstract = True
        ordering = ('is_admin', 'admin_order')
    

    def __unicode__(self):
        return "%s - %s" % (self.user, self.group,)

class GroupMemberManager(models.Manager):
    """
    Adds custom manager methods for accepted and bulk members.
    """
    use_for_related_fields = True
    def accepted(self):
        return self.get_query_set().filter(user__is_bulk=False)

    def bulk(self):
        return self.get_query_set().filter(user__is_bulk=True)

class GroupMember(BaseGroupMember):
    """
    Non-abstract representation of BaseGroupMember. Base class is required
    for GroupMemberRecord.
    """
    # had to double these two fields in this model and GroupMemberRecord due to issues with related_name. 
    # See http://docs.djangoproject.com/en/dev/topics/db/models/#be-careful-with-related-name
    group = models.ForeignKey(BaseGroup, related_name="members", verbose_name=_('group'))
    user = models.ForeignKey(User, related_name="member_groups", verbose_name=_('user'))
    # away = models.BooleanField(_('away'), default=False)
    # away_message = models.CharField(_('away_message'), max_length=500)
    # away_since = models.DateTimeField(_('away since'), default=datetime.now)

    objects = GroupMemberManager()

    @property
    def is_accepted(self):
        return not self.user.is_bulk

    @property
    def is_bulk(self):
        return self.user.is_bulk

class GroupMemberRecord(BaseGroupMember):
    """
    A snapshot of a user's group status at a particular point in time.
    """
    # had to double these two fields in this model and GroupMember due to issues with related_name. 
    # See http://docs.djangoproject.com/en/dev/topics/db/models/#be-careful-with-related-name
    group = models.ForeignKey(BaseGroup, related_name="member_records", verbose_name=_('group'))
    user = models.ForeignKey(User, related_name="group_records", verbose_name=_('user'))
    datetime = models.DateTimeField(auto_now_add=True)
    #datetime = models.DateTimeField(default=datetime.datetime.now())
    membership_start = models.BooleanField(default=False, help_text=_('Whether this record signifies the start of a membership or not.'))
    membership_end = models.BooleanField(default=False, help_text=_('Whether this record signifies the end of a membership or not.'))

    class Meta(BaseGroupMember.Meta):
        get_latest_by = 'datetime'

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(GroupMemberRecord, self).__init__(*args, **kwargs)
        if instance is not None:
            # copy over all properties from the instance provided
            # note that these override any values passed to the constructor
            self.group = instance.group
            self.user = instance.user
            self.is_admin = instance.is_admin
            self.admin_title = instance.admin_title
            self.admin_order = instance.admin_order
            self.joined = instance.joined
            self.datetime = instance.joined


def group_member_snapshot(sender, instance, created, **kwargs):
    """
    Takes a snapshot of a GroupMember object each time is
    saved.
    """
    record = GroupMemberRecord(instance=instance)
    if created:
        record.membership_start = True
    record.save()
post_save.connect(group_member_snapshot, sender=GroupMember, dispatch_uid='groupmembersnapshot')

def send_welcome_email(sender, instance, created, **kwargs):
    """
    Sends a welcome email to new members of a group
    """
    group = instance.group

    if created and group.welcome_email:
        user = instance.user
        
        sender = '"%s" <%s>' % (group.from_name, group.from_email)

        # TODO: template-ize
        txtMessage = """You have been added to the %s group on myEWB, the Engineers Without Borders online community.

"%s"
""" % (group.name, group.welcome_email)
         
        send_mail(subject="Welcome to '%s'" % group.name,
                  txtMessage=txtMessage, # TODO: make this text-only!
                  htmlMessage=None,
                  fromemail=sender,
                  recipients=[user.email])
        
post_save.connect(send_welcome_email, sender=GroupMember, dispatch_uid='groupmemberwelcomeemail')
        

def end_group_member_snapshot(sender, instance, **kwargs):
    """
    Takes the final snapshot of a group member as it is deleted.
    Sets the membership_end = True to signify the end.
    """
    record = GroupMemberRecord(instance=instance)
    record.membership_end = True
    record.save()
pre_delete.connect(end_group_member_snapshot, sender=GroupMember, dispatch_uid='endgroupmembersnapshot')
            
class PendingMember(models.Model):
    user = models.ForeignKey(User, related_name='pending_memberships')
    group = models.ForeignKey(BaseGroup, related_name='pending_members')
    request_date = models.DateField(auto_now_add=True)
    message = models.TextField(help_text=_("Message indicating reason for request."))

    @property
    def is_invited(self):
        return hasattr(self, 'invitationtojoingroup')

    @property
    def is_requested(self):
        return hasattr(self, 'requesttojoingroup')

    def accept(self):
        """
        Accepts the current request or invitation.
        """
        GroupMember.objects.create(user=self.user, group=self.group)
        self.delete()

    def reject(self):
        """
        Rejects the current request or invitation.
        """
        self.delete()

class RequestToJoinGroup(PendingMember):
    pass

class InvitationToJoinGroup(PendingMember):
    invited_by = models.ForeignKey(User, related_name='invitations_issued', default=0)

def invitation_notify(sender, instance, created, **kwargs):
    user = instance.user
    group = instance.group
    issuer = instance.invited_by
    message = instance.message
    
    if notification and False:  # need to create the notice type for this to work
        notification.send([user], "group_invite", {"invitation": instance})
    else:
        # TODO: templatize this
        # TODO: i18n this (trying to causes db errors right now)
        msgbody = "%s has invited you to join the \"%s\" group.<br/><br/>" % (issuer.visible_name(), group)
        if message:
            msgbody += message + "<br/><br/>"
        msgbody += "<a href='%s'>click here to respond</a>" % group.get_absolute_url()
        
        Message.objects.create(subject="%s has invited you to join the \"%s\" group" % (issuer.visible_name(), group),
                               body=msgbody,
                               sender=issuer,
                               recipient=user)

post_save.connect(invitation_notify, sender=InvitationToJoinGroup)
    
class GroupLocation(models.Model):
    group = models.ForeignKey(BaseGroup, related_name="locations", verbose_name=_('group'))
    place = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

def clean_up_bulk_users(sender, instance, created, **kwargs):
    if instance.verified:
        # XXX Warning! This only works because get_email_user returns
        # the user with their email set to the argument before it returns
        # users with EmailAddress's with the argument
        email_user = get_email_user(instance.email)
        user = instance.user
        # a 
        if email_user and not email_user == user:
            # update group memberships
            for membership in email_user.member_groups.all():
                if not user.member_groups.filter(group=membership.group):
                    membership.user = instance.user
                    membership.save()
                else:
                    membership.delete()
                    
            # update membership records (should we just delete them instead?)
            for record in email_user.group_records.all():
                record.user = instance.user
                record.save()
                
            # update invitations
            for invitation in email_user.pending_memberships.all():
                if not user.pending_memberships.filter(group=invitation.group):
                    invitation.user = instance.user
                    invitation.save()
                else:
                    invitation.delete()
                
            # delete old bulk user
            email_user.delete()

post_save.connect(clean_up_bulk_users, sender=EmailAddress)

def add_creator_to_group(sender, instance, created, **kwargs):
    # this is only a problem when loading sample data...
    try:
        creator = instance.creator
    except:
        creator = None
        
    if created and instance and creator:
        gm = GroupMember.objects.filter(user=creator,
                                        group=instance)
        if gm.count() == 0:
            GroupMember.objects.create(
                    user=creator, 
                    group=instance,
                    is_admin=True,
                    admin_title='%s Creator' % instance.name,
                    admin_order = 1)
post_save.connect(add_creator_to_group, sender=BaseGroup)
