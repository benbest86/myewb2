"""myEWB GroupTopics views

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Created on: 2009-08-13
Last modified: 2009-12-02
@author: Joshua Gorner, Francis Kung
"""

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.contrib.syndication import feeds
from django.shortcuts import get_object_or_404, render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.db.models import Q

from groups import bridge

from base_groups.models import BaseGroup
from group_topics.models import GroupTopic
from group_topics.forms import GroupTopicForm
from group_topics.feeds import TopicFeedAll, TopicFeedGroup
from threadedcomments.models import ThreadedComment

from attachments.forms import AttachmentForm
from attachments.models import Attachment
from topics.models import Topic
from wiki.models import Article

def topic(request, topic_id, group_slug=None, edit=False, template_name="topics/topic.html", bridge=None):

    topic = get_object_or_404(GroupTopic, id=topic_id)
    
    parent_group = topic.parent_group
    # XXX PERMISSIONS CHECK
    if not parent_group.is_visible(request.user) and not topic.creator == request.user:
        return HttpResponseForbidden()

    # XXX PERMISSIONS CHECK
    if (request.method == "POST" and edit == True and (request.user == topic.creator or request.user == topic.group.creator)):
        topic.body = request.POST["body"]
        topic.save()
        return HttpResponseRedirect(topic.get_absolute_url(group))

    # retrieve whiteboard (create if needed)
    if topic.whiteboard == None:
        # group_slug should always be valid - group never null!
        wb = Article(title="Post%d" % (topic.id), content="")
        if topic.group:
            topic.group.associate(wb, commit=False)
        wb.save()
        topic.whiteboard = wb
        topic.save()
        
    member = False
    if topic.group and topic.group.user_is_member(request.user):
        member = True

    return render_to_response(template_name, {
        "topic": topic,
        "edit": edit,
        "group": topic.group,
        "member": member,
    }, context_instance=RequestContext(request))

def topics(request, group_slug=None, form_class=GroupTopicForm, attach_form_class=AttachmentForm, template_name="topics/topics.html", bridge=None):
    
    is_member = False
    group = None
    if group_slug is not None:
        group = get_object_or_404(BaseGroup, slug=group_slug)
        is_member = group.user_is_member(request.user)
    
    attach_count = 0
    if request.method == "POST" and group:
        try:
            attach_count = int(request.POST.get("attach_count", 0))
        except ValueError:
            attach_count = 0
            
        if request.user.is_authenticated():
            if is_member:
                topic_form = form_class(request.POST)
                attach_forms = [attach_form_class(request.POST, request.FILES, prefix=str(x), instance=Attachment()) for x in range(0,attach_count)]
                
                # do not take blank attachment forms into account
                for af in attach_forms:
                    if not af.is_valid() and not af['attachment_file'].data:
                        attach_forms.remove(af)
                        attach_count = attach_count - 1
                
                if topic_form.is_valid() and all([af.is_valid() for af in attach_forms]):
                    topic = topic_form.save(commit=False)
                    if group:
                        group.associate(topic, commit=False)
                    topic.creator = request.user
                    topic.save()
                    
                    # We need the "Topic" object in order to retrieve attachments properly
                    # since other functions only get the Topic object
                    base_topic = GroupTopic.objects.get(id=topic.id)
                    for af in attach_forms:
                        attachment = af.save(request, base_topic)

                    topic.send_email()
                        
                    request.user.message_set.create(message=_("You have started the topic %(topic_title)s") % {"topic_title": topic.title})
                    topic_form = form_class(instance=GroupTopic()) # @@@ is this the right way to reset it?                    
                    attach_forms = [attach_form_class(prefix=str(x), instance=Attachment()) for x in range(0,attach_count)]
            else:
                request.user.message_set.create(message=_("You are not a member and so cannot start a new topic"))
                topic_form = form_class(instance=GroupTopic())                
                attach_forms = [attach_form_class(prefix=str(x), instance=Attachment()) for x in range(0,attach_count)]
        else:
            return HttpResponseForbidden()
    else:
        topic_form = form_class(instance=GroupTopic())
        attach_forms = []
    
    if group:
        if group.is_visible(request.user):
            topics = GroupTopic.objects.get_for_group(group)
        else:
            return HttpResponseForbidden()

    else:
        if request.user.is_authenticated():
            # generic topic listing: show posts from groups you're in
            # TODO: do we want to also show posts from public groups?
            topics = GroupTopic.objects.filter(parent_group__member_users=request.user)

        else:
            # for guests, show all posts from public groups
            topics = GroupTopic.objects.visible()
            
    return render_to_response(template_name, {
        "group": group,
        "topic_form": topic_form,
        "attach_forms": attach_forms,
        "attach_count": attach_count,
        "is_member": is_member,
        "topics": topics,
    }, context_instance=RequestContext(request))

def feed(request, group_slug):
    try:
        if group_slug == 'all':
            feedgen = TopicFeedAll(group_slug, request).get_feed()
        else:
            group = BaseGroup.objects.get(slug=group_slug)
            if group.is_visible(request.user):
                feedgen = TopicFeedGroup(group_slug, request).get_feed(group_slug)
            else:
                return HttpResponseForbidden()

    except feeds.FeedDoesNotExist:
        raise Http404, _("Invalid feed parameters. Slug %r is valid, but other parameters, or lack thereof, are not.") % slug

    response = HttpResponse(mimetype=feedgen.mime_type)
    feedgen.write(response, 'utf-8')
    return response

def get_attachment_form(request, template_name="topics/attachment_form.html", form_class=AttachmentForm, group_slug=None, bridge=None):

    if request.is_ajax():
        attach_form = form_class(prefix=request.POST['prefix'], instance=Attachment())
        response = render_to_response(
            template_name,
            {
                'attach_form': attach_form,
            },
            context_instance=RequestContext(request),
        )
        return response


def topic_delete(request, topic_id, group_slug=None, bridge=None):
    """
    Another copy-pasta from pinax.apps.topics.views.
    Again need to update to match our GroupTopic stuff.
    Mostly we 
    """
    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    if group:
        topics = group.content_objects(Topic)
    else:
        # line below is the only change between pinax and us.
        # topics = Topic.objects.filter(object_id=None)
        topics = Topic.objects.all()

    
    topic = get_object_or_404(topics, id=topic_id)
    
    if (request.method == "POST" and (request.user == topic.creator or request.user == topic.group.creator)):
        ThreadedComment.objects.all_for_object(topic).delete()
        topic.delete()
    
    return HttpResponseRedirect(request.POST["next"])

def topics_by_user(request, username):
    """
    Return a listing of all topics visible the current user, and created by
    the given user
    """
    user = get_object_or_404(User, username=username)

    if request.user == user:
        # user can always see their own post, regardless of group visibility
        # (ie, if I write some posts to a private group then leave the group, 
        #  those posts should still show in this listing)
        topics = GroupTopic.objects.get_for_user(user)
        
    else:
        # start with all visible topics
        topics = GroupTopic.objects.visible(request.user)
            
        # then restrict further to only ones by the given user
        topics = GroupTopic.objects.get_for_user(user, topics)
            
    return render_to_response("topics/topics.html",
                              {"topics": topics},
                              context_instance=RequestContext(request)
                             )
