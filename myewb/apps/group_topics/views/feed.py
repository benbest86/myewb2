"""myEWB GroupTopics RSS feeds

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

from django.contrib.syndication import feeds
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404
from tagging.models import Tag, TaggedItem

from base_groups.models import BaseGroup
from group_topics.feeds import TopicFeedAll, TopicFeedGroup, TopicFeedFeatured, TopicFeedTag

def group(request, group_slug):
    try:
        try:
            group = BaseGroup.objects.get(slug=group_slug)
        except:
            group = BaseGroup.objects.get(id=int(group_slug))
            group_slug = group.slug
        
        # concept of a RSS feed for a logged-in user is weird, but OK...
        if group.is_visible(request.user):
            feedgen = TopicFeedGroup(group_slug, request).get_feed(group_slug)
        else:
            return HttpResponseForbidden()

    except feeds.FeedDoesNotExist:
        raise Http404, _("Invalid feed parameters. Slug %r is valid, but other parameters, or lack thereof, are not.") % slug

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
