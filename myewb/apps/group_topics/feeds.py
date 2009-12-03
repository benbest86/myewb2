"""myEWB GroupTopics feeds

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Created on: 2009-08-11
Last modified: 2009-08-15
@author: Joshua Gorner, Francis Kung
"""

from atomformat import Feed
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404
from group_topics.models import GroupTopic
from base_groups.models import BaseGroup
from django.template.defaultfilters import linebreaks, escape, capfirst
from datetime import datetime
from friends.models import friend_set_for
from django.contrib.contenttypes.models import ContentType
from base_groups.urls import bridge as temp_bridge

ITEMS_PER_FEED = getattr(settings, 'PINAX_ITEMS_PER_FEED', 20)

class BaseTopicFeed(Feed):
    def item_id(self, topic):
        return "http://%s%s" % (
            Site.objects.get_current().domain,
            topic.get_absolute_url(),
        )
    
    def item_title(self, topic):
        return topic.title
    
    def item_updated(self, topic):
        return topic.modified
    
    def item_published(self, topic):
        return topic.created
    
    def item_content(self, topic):
        return {"type" : "html", }, linebreaks(escape(topic.body))
    
    def item_links(self, topic):
        return [{"href" : self.item_id(topic)}]
    
    def item_authors(self, topic):
        return [{"name" : topic.creator.get_profile().name}]

class TopicFeedAll(BaseTopicFeed):
    def feed_id(self):
        return 'http://%s%s' % (Site.objects.get_current().domain,
                                reverse('topic_feed', kwargs={'group_slug': 'all'}))
    
    def feed_title(self):
        return 'Post feed for all groups'

    def feed_updated(self):
        qs = GroupTopic.objects.filter(parent_group__visibility='E')
        # We return an arbitrary date if there are no results, because there
        # must be a feed_updated field as per the Atom specifications, however
        # there is no real data to go by, and an arbitrary date can be static.
        if qs.count() == 0:
            return datetime(year=2008, month=7, day=1)
        return qs.latest('created').created

    def feed_links(self):
        absolute_url = reverse('topic_list')
        complete_url = "http://%s%s" % (
                Site.objects.get_current().domain,
                absolute_url,
            )
        return ({'href': complete_url},)

    def items(self):
        return GroupTopic.objects.filter(parent_group__visibility='E').order_by("-created")[:ITEMS_PER_FEED]

class TopicFeedGroup(BaseTopicFeed):
    def get_object(self, params):
        return get_object_or_404(BaseGroup, slug=params[0].lower())
    
    def feed_id(self, group):
        return 'http://%s%s' % (Site.objects.get_current().domain,
                                reverse('topic_feed', kwargs={'group_slug': group.slug}))

    def feed_title(self, group):
        return 'Post feed for %s %s' % (group.model.lower(), group.slug)

    def feed_updated(self, group):
        qs = GroupTopic.objects.filter(object_id=group.id)
        # We return an arbitrary date if there are no results, because there
        # must be a feed_updated field as per the Atom specifications, however
        # there is no real data to go by, and an arbitrary date can be static.
        if qs.count() == 0:
            return datetime(year=2008, month=7, day=1)
        return qs.latest('created').created

    def feed_links(self, group):
        model = ContentType.objects.get(model=group.model.lower()).model_class()
        group = model.objects.get(slug=group.slug)
        absolute_url = group.content_bridge.reverse("topic_list", group)
        complete_url = "http://%s%s" % (
                Site.objects.get_current().domain,
                absolute_url,
            )
        return ({'href': complete_url},)

    def items(self, group):
        # NOTE: security needs to be handled elsewhere!!!
        # (ie, currently, in group_topics.views.feed())
        return GroupTopic.objects.filter(object_id=group.id).order_by("-created")[:ITEMS_PER_FEED]