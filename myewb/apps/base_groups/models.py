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
from django.db.models.signals import post_save
from django.core.mail import EmailMessage

from emailconfirmation.models import EmailAddress

from siteutils.helpers import get_email_user
from groups.base import Group
from wiki.models import Article

class BaseGroup(Group):
    """Base group (from which networks, communities, projects, etc. derive).
    
    Not intended to be instantiated by itself.
    """
    
    model = models.CharField(_('group model'), max_length=500, null=True, blank=True)
    parent = models.ForeignKey('self', related_name="children", verbose_name=_('parent'), null=True, blank=True)
    
    member_users = models.ManyToManyField(User, through="GroupMember", verbose_name=_('members'))
	
	# private means members can only join if invited
    private = models.BooleanField(_('private'), default=False)
    
    VISIBILITY_CHOICES = (
        ('E', _("everyone")),
        ('P', _("group members and members of parent network only")),
        ('M', _("group members only"))
    )
    visibility = models.CharField(_('visibility'), max_length=1, choices=VISIBILITY_CHOICES, default='E')
    
    whiteboard = models.ForeignKey(Article, related_name="group", verbose_name=_('whiteboard'), null=True)
    
    def is_visible(self, user):
        visible = False
        if self.visibility == 'E':
            visible = True
        elif user.is_authenticated():
            if user.is_superuser:
                return True
            
            member_list = self.members.filter(user=user, request_status='A')
            if member_list.count() > 0:
                visible = True
            elif self.visibility == 'P':
                parent_member_list = self.parent.members.filter(user=user, request_status='A')
                if parent_member_list.count() > 0:
                    visible = True
        return visible
	
    def user_is_member(self, user):
        return user.is_authenticated() and (self.members.filter(user=user, request_status='A').count() > 0)
        
    def user_is_member_or_pending(self, user):
        return user.is_authenticated() and (self.members.filter(user=user).count() > 0)
            
    def user_is_admin(self, user):
        return user.is_authenticated() and \
            ((self.members.filter(user=user, request_status='A', is_admin=True).count() > 0) or user.is_superuser)

    def get_absolute_url(self):
        return reverse('group_detail', kwargs={'group_slug': self.slug})

    def get_member_emails(self):
        members_with_emails = self.get_accepted_members().select_related(depth=1).exclude(user__email='') | \
                self.members.filter(request_status='B').select_related(depth=1)
        return [member.user.email for member in members_with_emails]

    def add_member(self, user):
        """
        Adds a member to a group with the proper request_status.
        """
        request_status = user.has_usable_password() and 'A' or 'B'
        return GroupMember.objects.create(user=user, group=self, request_status=request_status)

    def send_mail_to_members(self, subject, body, html=True, fail_silently=False):
        """
        Creates and sends an email to all members of a network using Django's
        EmailMessage.
        Takes in a a subject and a message and an optional fail_silently flag.
        Automatically sets:
        from_email: group_name <group_slug@ewb.ca>
        to: list-group_slug@ewb.ca
        bcc: list of member emails
        """
        msg = EmailMessage(
                subject=subject, 
                body=body, 
                from_email='%s <%s@ewb.ca>' % (self.name, self.slug), 
                to=['list-%s@ewb.ca' % self.slug],
                bcc=self.get_member_emails(),
                )
        if html:
            msg.content_subtype = "html"
        msg.send(fail_silently=fail_silently)
	
	# TODO:
	# list of members (NOT CSV)

    def save(self, force_insert=False, force_update=False):
        # if we are updating a group, don't change the slug (for consistency)
        if not self.id:
            slug = self.slug
            slug = slug.replace(' ', '-')
            
            # translates accents into their regular-character equivalent
            # (http://snippets.dzone.com/posts/show/5499)
            slug = unicodedata.normalize('NFKD', unicode(slug)).encode('ASCII', 'ignore')
            
            # FIXME: anything else we need to escape??
            #(?P<group_slug>[-\w]+) yes, lots of things. This is the
            # regex definition of a slug so if we don't match on this we 
            # should remove illegal characters.
            match = re.match(r'[-\w]+', slug)
            if match is None or not match.group(0) == slug:
                slug = re.sub(r'[^-\w]+', '', slug)
            
            # check if slug is in use; increment until we find a good one.
            # (is there anything better than numerical incrementing?)
            temp_groups = BaseGroup.objects.filter(slug__contains=slug, model=self.model)

            if (temp_groups.count() != 0):
                slugs = [n.slug for n in temp_groups]
                old_slug = slug
                i = 0
                while slug in slugs:
                    i = i + 1
                    slug = old_slug + "%d" % (i, )
            self.slug = slug
        super(BaseGroup, self).save(force_insert=force_insert, force_update=force_update)

    def get_url_kwargs(self):
        return {'group_slug': self.slug}
        
    def get_visible_children(self, user):
        if not user.is_authenticated():
            return self.children.filter(visibility='E')
        elif user.is_superuser:
            return self.children.all()
        else:
            children = self.children.filter(visibility='E') | self.children.filter(member_users=user)
            if self.user_is_member(user):
                children = children | self.children.filter(visibility='P')
            return children.distinct()
            
    def get_accepted_members(self):
        return self.members.filter(request_status='A')

	
class GroupMember(models.Model):
    group = models.ForeignKey(BaseGroup, related_name="members", verbose_name=_('group'))
    user = models.ForeignKey(User, related_name="member_groups", verbose_name=_('user'))
    is_admin = models.BooleanField(_('admin'), default=False)
    admin_title = models.CharField(_('admin title'), max_length=500, null=True, blank=True)
    admin_order = models.IntegerField(_('admin order (smallest numbers come first)'), default=999)
    joined = models.DateTimeField(_('joined'), default=datetime.datetime.now)
    
    REQUEST_STATUS_CHOICES = (
        ('A', _("accepted")),
        ('I', _("invited")),
        ('R', _("requested")),
        ('B', _("bulk member")),
    )
    request_status = models.CharField(_('request status'), max_length=1, choices=REQUEST_STATUS_CHOICES, default='A')
    
    def is_accepted(self):
        return self.request_status == 'A'
    
    def is_invited(self):
        return self.request_status == 'I'
        
    def is_requested(self):
        return self.request_status == 'R'

    def is_bulk(self):
        return self.request_status == 'B'
        
    def change_status(self, status_string=None):
        # end any existing statuses
        old_gsrs = GroupStatusRecord.objects.filter(user=self.user, group=self.group, end=None)
        for old_gsr in old_gsrs:
            old_gsr.end = datetime.datetime.now()
            old_gsr.save()
        
        # status_string == None implies user is leaving group
        if status_string:
            gsr = GroupStatusRecord(user=self.user, group=self.group, status=status_string)
            gsr.save()        
        
    def save(self, force_insert=False, force_update=False):        
        if(self.id):
            prev = GroupMember.objects.get(pk=self.id)
            
            if prev.is_bulk and not self.is_bulk:
                self.change_status("recipient")            
            elif not prev.is_accepted and self.is_accepted:
                self.change_status("regular")            
            elif not prev.is_admin and self.is_admin:
                self.change_status("admin")
            elif prev.is_admin == True and not self.is_admin:
                self.change_status("regular")                
                
        else:
            if self.is_accepted:
                self.change_status("regular")
            
            elif self.is_admin:
                self.change_status("admin")
                
            elif self.is_bulk and not self.is_accepted:       # weird bug - the first really should imply the other
                # Assuming for now that "recipient" covers mailing-list-only members
                # This may differ slightly from what's been assumed in myEWB previously
                self.change_status("recipient")
        
        super(GroupMember, self).save(force_insert, force_update)
        
    def delete(self):
        self.change_status()    # i.e. end current status(es)
        
        super(GroupMember, self).delete()
    
    class Meta:
        ordering = ('is_admin', 'admin_order')
        
    def __unicode__(self):
        return "%s - %s (%s)" % (self.user, self.group, self.request_status)
        
    # away = models.BooleanField(_('away'), default=False)
    # away_message = models.CharField(_('away_message'), max_length=500)
    # away_since = models.DateTimeField(_('away since'), default=datetime.now)

class GroupStatusRecord(models.Model):
    group = models.ForeignKey(BaseGroup, related_name="status_records", verbose_name=_('group'))    
    user = models.ForeignKey(User, related_name="status_records", verbose_name=_('user'))
    status = models.CharField(max_length=100, null=True, blank=True)
    start = models.DateTimeField(_('start'), default=datetime.datetime.now)
    end = models.DateTimeField(_('end'), null=True, blank=True)
    
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
        if not email_user == user:
            for membership in email_user.member_groups.all():
                if membership.request_status == 'B' and not user.member_groups.filter(group=membership.group):
                    membership.user = instance.user
                    membership.request_status = 'A'
                    membership.save()
            # delete old bulk user - should delete GroupMember objects as well
            email_user.delete()

post_save.connect(clean_up_bulk_users, sender=EmailAddress)

def add_creator_to_group(sender, instance, created, **kwargs):
    if created:
        try:
            GroupMember.objects.create(
                    user=instance.creator, 
                    group=instance,
                    is_admin=True,
                    admin_title='%s Creator' % instance.name,
                    admin_order = 1)
        except:
            pass
post_save.connect(add_creator_to_group, sender=BaseGroup)
