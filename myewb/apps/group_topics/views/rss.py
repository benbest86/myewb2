"""myEWB GroupTopics RSS feeds

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

from django.conf import settings
from django.contrib.syndication.feeds import Feed
from group_topics.models import GroupTopic

ITEMS_PER_FEED = getattr(settings, 'PINAX_ITEMS_PER_FEED', 20)

class RSSAllPosts(Feed):
    title = "myEWB - Engineers Without Borders Canada"
    link = "/rss/posts"
    description = "Discussions in Engineers Without Borders Canada"
    
    description_template = "topics/rss.html"

    def items(self):
        return GroupTopic.objects.visible()[:ITEMS_PER_FEED]
