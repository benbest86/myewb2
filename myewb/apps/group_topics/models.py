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
from topics.models import Topic
from wiki.models import Article

from lxml.html.clean import clean_html, autolink_html

class GroupTopicManager(models.Manager):

    def visible(self, user=None):
        """
        Returns visible posts by group visibility. Takes an optional
        user parameter which adds GroupTopics from groups that the
        member is a part of.
        """
        filter_q = Q(parent_group__visibility='E')
        if user is not None and not user.is_anonymous():
            filter_q |= Q(parent_group__member_users=user)
        return self.get_query_set().filter(filter_q)
    
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
        if group:
            return group.content_bridge.reverse("topic_detail", group, kwargs=kwargs)
        else:
            return reverse("topic_detail", kwargs=kwargs)
        
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
        
    class Meta:
        ordering = ('-modified', )
