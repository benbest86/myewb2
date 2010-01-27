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
from django.core.urlresolvers import reverse
from django.template import Context, loader

from attachments.models import Attachment
from base_groups.models import BaseGroup
from base_groups.helpers import user_can_adminovision, user_can_execovision
from topics.models import Topic
from wiki.models import Article

from lxml.html.clean import clean_html, autolink_html

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

class GroupTopic(Topic):
    """
    a discussion topic for a BaseGroup.
    """
    
    parent_group = models.ForeignKey(BaseGroup, related_name="topics", verbose_name=_('parent'))
    send_as_email = models.BooleanField(_('send as email'), default=False)
    whiteboard = models.ForeignKey(Article, related_name="topic", verbose_name=_('whiteboard'), null=True)

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
    
    def send_email(self):
        if self.send_as_email:
            attachments = Attachment.objects.attachments_for_object(self)
            
            tmpl = loader.get_template("email_template.html")
            c = Context({'group': self.group,
                         'title': self.title,
                         'body': self.body,
                         'topic_id': self.pk,
                         'attachments': attachments
                         })
            message = tmpl.render(c)
    
            self.group.send_mail_to_members(self.title, message)
        
    def num_whiteboard_edits(self):
        if self.whiteboard:
            return self.whiteboard.changeset_set.count()
        else:
            return 0
            
    def intro(self):
        if len(self.body) < 600:
            return self.body

        # thanks http://stackoverflow.com/questions/250357/smart-truncate-in-python
        return self.body[:600].rsplit(' ', 1)[0]+"..."
    
    def intro_has_more(self):
        return (len(self.body) >= 600)

    class Meta:
        ordering = ('-modified', )
        
