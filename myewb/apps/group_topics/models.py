"""myEWB GroupTopic models

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Created on: 2009-08-13
@author: Joshua Gorner
"""

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.template import Context, loader

from attachments.models import Attachment
from base_groups.models import BaseGroup
from base_groups.helpers import user_can_adminovision, user_can_execovision
from topics.models import Topic
from whiteboard.models import Whiteboard

from lxml.html.clean import clean_html, autolink_html, Cleaner

class GroupTopicManager(models.Manager):

    def visible(self, user=None):
        """
        Returns visible posts by group visibility. Takes an optional
        user parameter which adds GroupTopics from groups that the
        member is a part of. Handles AnonymousUser instances
        transparently
        """
        filter_q = Q(parent_group__visibility='E')
        if user is not None and not user.is_anonymous():
            
            # admins with admin-o-vision on automatically see everything
            if user_can_adminovision(user) and user.get_profile().adminovision == 1:
                return self.get_query_set()
            
            # and similar for exec-o-vision, except only for your own chapter's groups
            if user_can_execovision(user) and user.get_profile().adminovision == 1:
                filter_q |= Q(parent_group__parent__members__user=user,
                              parent_group__parent__members__is_admin=True)
            
            # everyone else only sees stuff from their own groups
            filter_q |= Q(parent_group__member_users=user)

        # would it be more efficient to remove the OR query above and just write
        # two different queries, instead of using distinct() here?
        return self.get_query_set().filter(filter_q).distinct()
    
    def get_for_group(self, group):
        """
        Returns all posts belonging to a given group
        """
        return self.get_query_set().filter(parent_group=group)
    
    def get_for_user(self, user, qs=None):
        """
        Returns all posts belonging to a given user.  If passed the optional 
        qs parameter, it will filter that queryset instead of creating a new one.
        """
        if qs == None:
            qs = self.get_query_set()
        return qs.filter(creator=user)
    
    def get_for_watchlist(self, watchlist, qs=None):
        """
        Returns all posts contained in a given watchlist.  If passed the optional 
        qs parameter, it will filter that queryset instead of creating a new one.
        """
        if qs == None:
            qs = self.get_query_set()
        return qs.filter(watchlists=watchlist)
    
    def featured(self, qs=None, user=None):
        """
        Returns a list of featured posts, based on post scores.  If passed the 
        optional qs parameter, it will filter that queryset instead of creating 
        a new one.
        """
        if qs == None:
            qs = self.visible(user)
        return qs.order_by('-score')
    
    def since(self, date, qs=None, user=None):
        """
        Returns a list of posts since the given date.  If passed the 
        optional qs parameter, it will filter that queryset instead of creating 
        a new one.
        """
        if qs == None:
            qs = self.visible(user)
        return qs.filter(created__gt=date).order_by('created')
    
    def replies_since(self, date, qs=None, user=None):
        """
        Returns a list of posts with replies since the given date.  If passed the 
        optional qs parameter, it will filter that queryset instead of creating 
        a new one.
        """
        if qs == None:
            qs = self.visible(user)
        return qs.filter(last_reply__gt=date).order_by('last_reply')
    
class GroupTopic(Topic):
    """
    a discussion topic for a BaseGroup.
    """
    
    parent_group = models.ForeignKey(BaseGroup, related_name="topics", verbose_name=_('parent'))
    send_as_email = models.BooleanField(_('send as email'), default=False)
    whiteboard = models.ForeignKey(Whiteboard, related_name="topic", verbose_name=_('whiteboard'), null=True)
    
    last_reply = models.DateTimeField(_('last reply'), editable=False, blank=True, null=True)
    
    # possibly split these out into a different table so we can optimize it?
    # (would we lose the benefits due to the join though?)
    score = models.IntegerField(editable=False, default=0, db_index=True)
    score_modifier = models.IntegerField(_("score modifier"), default=100)
    
    objects = GroupTopicManager()
    
    def get_absolute_url(self, group=None):
        kwargs = {"topic_id": self.pk}
        return reverse("topic_detail", kwargs=kwargs)
    
    def is_visible(self, user):
        if self.creator == user:
            return True
        else:
            return self.parent_group.is_visible(user)

    def is_editable(self, user):
        return user == self.creator or self.parent_group.user_is_admin(user)
        
    def save(self, force_insert=False, force_update=False):
        # validate HTML content
        # Additional options at http://codespeak.net/lxml/lxmlhtml.html#cleaning-up-html
        self.body = clean_html(self.body)
        self.body = autolink_html(self.body)
        
        # set parent group
        group = BaseGroup.objects.get(id=self.object_id)
        self.parent_group = group
        
        super(GroupTopic, self).save(force_insert, force_update)
        post_save.send(sender=Topic, instance=GroupTopic.objects.get(id=self.id))
    
    def send_email(self, sender=None):
        attachments = Attachment.objects.attachments_for_object(self)
        
        tmpl = loader.get_template("email_template.html")
        c = Context({'group': self.group,
                     'title': self.title,
                     'body': self.body,
                     'topic_id': self.pk,
                     'attachments': attachments
                     })
        message = tmpl.render(c)
    
        if self.send_as_email:
            self.group.send_mail_to_members(self.title, message, sender=sender)
        
        for list in self.watchlists:
            user = list.owner
            # TODO: for user in list.subscribers blah blah
            sender = 'myEWB <notices@my.ewb.ca>'
    
            msg = EmailMessage(subject=self.title,
                               body=message,
                               from_email=sender, 
                               to=user.email
                              )
            msg.send(fail_silently=False)
        
    def num_whiteboard_edits(self):
        if self.whiteboard:
            return self.whiteboard.changeset_set.count()
        else:
            return 0
            
    def intro(self):
        if len(self.body) < 600:
            return self.body

        # thanks http://stackoverflow.com/questions/250357/smart-truncate-in-python
        intro = self.body[:600].rsplit(' ', 1)[0]

        intro = Cleaner(scripts=False,      # disable it all except page_structure
                        javascript=False,   # as proper cleaning is done on save;
                        comments=False,     # here we just want to fix any
                        links=False,        # dangling tags caused by truncation
                        meta=False,
                        #page_stricture=True,
                        embedded=False,
                        frames=False,
                        forms=False,
                        annoying_tags=False,
                        remove_unknown_tags=False,
                        safe_attrs_only=False).clean_html(intro)
        
        intro += "..."
        return intro
    
    def intro_has_more(self):
        return (len(self.body) >= 600)
    
    def update_score(self, amount):
        self.score += int(amount * (self.score_modifier / float(100)))
        self.save()

    def update_modifier(self, new_modifier):
        difference = float(new_modifier) / float(self.score_modifier)
        self.score = int(self.score * difference)
        self.score_modifier = new_modifier
        self.save()

    class Meta:
        ordering = ('-modified', )
        verbose_name = "post"
        
class Watchlist(models.Model):
    name = models.CharField(_('name'), max_length=255)
    owner = models.ForeignKey(User, related_name="watchlists", verbose_name=_('owner'))

    subscribers = models.ManyToManyField(User,
                                         related_name="watchlists_subscribed",
                                         blank=True)
    posts = models.ManyToManyField(GroupTopic,
                                   related_name="watchlists",
                                   blank=True)
    
    def user_can_control(self, user):
        return user == self.owner
    
    def add_post(self, post):
        self.posts.add(post)
        
    def remove_post(self, post):
        self.posts.remove(post)

    def post_on_list(self, post):
        qs = self.posts.filter(pk=post.pk)
        if qs.count() > 0:
            return True
        else:
            return False
