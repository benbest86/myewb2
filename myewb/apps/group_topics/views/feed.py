"""myEWB GroupTopics atom feeds

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

from django.contrib.syndication import feeds
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, HttpResponsePermanentRedirect, Http404
from tagging.models import Tag, TaggedItem

from base_groups.models import BaseGroup
from group_topics.feeds import TopicFeedAll, TopicFeedGroup, TopicFeedFeatured, TopicFeedTag

def group(request, group_slug):
    key = request.GET.get('key', None)
    
    if group_slug == "waterloo":        # legacy name...
        return HttpResponsePermanentRedirect(reverse('topic_feed_group', kwargs={'group_slug': 'grandriver'}))
        
    try:
        try:
            group = BaseGroup.objects.get(slug=group_slug)
        except:
            try:
                group = BaseGroup.objects.get(id=int(group_slug))
            except:
                raise feeds.FeedDoesNotExist
            group_slug = group.slug

        # allow access by restricted key, so that you can put the RSS feed
        # of a private group onto a website somewhere...
        if key and key == group.secret_key:
            feedgen = TopicFeedGroup(group_slug, request).get_feed(group_slug)
        
        # concept of a RSS feed for a logged-in user is weird, but OK...
        elif group.is_visible(request.user):
            feedgen = TopicFeedGroup(group_slug, request).get_feed(group_slug)
        else:
            return HttpResponseForbidden()

    except feeds.FeedDoesNotExist:
        raise Http404, "Not found."

    response = HttpResponse(mimetype=feedgen.mime_type)
    feedgen.write(response, 'utf-8')
    return response

def all(request):
    feedgen = TopicFeedAll(None, request).get_feed()
    
    response = HttpResponse(mimetype=feedgen.mime_type)
    feedgen.write(response, 'utf-8')
    return response

def tag(request, tag):
    feedgen = TopicFeedTag(tag, request).get_feed(tag)
    response = HttpResponse(mimetype=feedgen.mime_type)
    feedgen.write(response, 'utf-8')
    return response
    try:
        tag = Tag.objects.get(name=tag)
        feedgen = TopicFeedTag(tag, request).get_feed(tag)
        response = HttpResponse(mimetype=feedgen.mime_type)
        feedgen.write(response, 'utf-8')
        return response
    except:
        return HttpResponse("")
    
def featured(request):
    feedgen = TopicFeedFeatured(None, request).get_feed()
    
    response = HttpResponse(mimetype=feedgen.mime_type)
    feedgen.write(response, 'utf-8')
    return response
