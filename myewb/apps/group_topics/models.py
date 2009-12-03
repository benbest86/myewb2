"""myEWB GroupTopic models

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Created on: 2009-08-13
@author: Joshua Gorner
"""

from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from base_groups.models import BaseGroup
from topics.models import Topic
from wiki.models import Article

from lxml.html.clean import clean_html, autolink_html

class GroupTopic(Topic):
    """
    a discussion topic for a BaseGroup.
    """
    
    parent_group = models.ForeignKey(BaseGroup, related_name="topics", verbose_name=_('parent'))
    send_as_email = models.BooleanField(_('send as email'), default=False)
    whiteboard = models.ForeignKey(Article, related_name="topic", verbose_name=_('whiteboard'), null=True)
    
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
    
    class Meta:
        ordering = ('-modified', )

def send_topic_email(sender, instance, **kwargs):
    if instance.send_as_email:
        instance.group.send_mail_to_members(instance.title, instance.body)
models.signals.post_save.connect(send_topic_email, sender=GroupTopic)
