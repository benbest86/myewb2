"""myEWB GroupTopics RSS feeds

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

import datetime

from django.conf import settings
from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Rss201rev2Feed, rfc2822_date
from group_topics.models import GroupTopic

ITEMS_PER_FEED = getattr(settings, 'PINAX_ITEMS_PER_FEED', 20)

class RssFeedWithPubDate(Rss201rev2Feed):
    def add_root_elements(self, handler):
        super(RssFeedWithPubDate, self).add_root_elements(handler)
        handler.addQuickElement('pubDate', rfc2822_date(self.latest_post_date()).decode('utf-8'))
    
class RSSAllPosts(Feed):
    title = "myEWB - Engineers Without Borders Canada"
    link = "/"
    description = "Discussions in Engineers Without Borders Canada"
    feed_type = RssFeedWithPubDate
    
    description_template = "topics/rss.html"

    def items(self):
        return GroupTopic.objects.visible()[:ITEMS_PER_FEED]

    def item_pubdate(self, item):
        return item.last_reply
