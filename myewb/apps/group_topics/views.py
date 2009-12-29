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
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.db.models import Q

from groups import bridge

from base_groups.models import BaseGroup
from base_groups.helpers import user_can_adminovision
from group_topics.models import GroupTopic
from group_topics.forms import GroupTopicForm
from group_topics.feeds import TopicFeedAll, TopicFeedGroup
from threadedcomments.models import ThreadedComment
from profiles.models import MemberProfile

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
    # only the owner of a topic or a group admin can edit a topic (??)
    if (request.method == "POST" and edit == True and \
            topic.is_editable(request.user)):
        updated_body = request.POST.get('body', None)
        if updated_body is not None:
            topic.body = updated_body
            topic.save()
        return HttpResponseRedirect(topic.get_absolute_url())

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
        is_member = group.user_is_member(request.user, admin_override=True)

    if group and not group.is_visible(request.user):
        return HttpResponseForbidden()
    
    attach_count = 0
    if request.method == "POST" and group:
        if not request.user.is_authenticated():
            return HttpResponseForbidden()
        try:
            attach_count = int(request.POST.get("attach_count", 0))
        except ValueError:
            attach_count = 0
            
        if is_member:
            topic_form = form_class(request.POST)
            attach_forms = [attach_form_class(request.POST, request.FILES, prefix=str(x), instance=Attachment()) for x in range(0,attach_count)]
            
            # do not take blank attachment forms into account
            for af in attach_forms:
                if not af.is_valid() and not af['attachment_file'].data:
                    attach_forms.remove(af)
                    attach_count = attach_count - 1
            
            # all good.  save it!
            if topic_form.is_valid() and all([af.is_valid() for af in attach_forms]):
                topic = topic_form.save(commit=False)
                if group:
                    group.associate(topic, commit=False)
                topic.creator = request.user
                topic.save()
                
                # save the attachment.
                # We need the "Topic" object in order to retrieve attachments properly
                # since other functions only get the Topic object
                base_topic = GroupTopic.objects.get(id=topic.id)
                for af in attach_forms:
                    attachment = af.save(request, base_topic)

                topic.send_email()
                    
                # redirect out.
                request.user.message_set.create(message=_("You have started the topic %(topic_title)s") % {"topic_title": topic.title})
                return HttpResponseRedirect(topic.get_absolute_url())
        else:
            # if they can't start a topic, why are we still loading up a form?
            request.user.message_set.create(message=_("You are not a member and so cannot start a new topic"))
            topic_form = form_class(instance=GroupTopic())                
            attach_forms = [attach_form_class(prefix=str(x), instance=Attachment()) for x in range(0,attach_count)]
    else:
        topic_form = form_class(instance=GroupTopic())
        attach_forms = []
    
    # if it's a listing by group, check group visibility
    if group:
        topics = GroupTopic.objects.get_for_group(group)

    # otherwise throw up a generic listing of visible posts
    else:
        # generic topic listing: show posts from groups you're in
        # also shows posts from public groups...
        # for guests, show posts from public groups only
        topics = GroupTopic.objects.visible(user=request.user)

    if request.user.is_authenticated():
        can_adminovision = user_can_adminovision(request.user)
        adminovision = request.user.get_profile().adminovision
    else:
        can_adminovision = False
        adminovision = False
            
    return render_to_response(template_name, {
        "group": group,
        "topic_form": topic_form,
        "attach_forms": attach_forms,
        "attach_count": attach_count,
        "is_member": is_member,
        "topics": topics,
        "can_adminovision": can_adminovision,
        "adminovision": adminovision,
    }, context_instance=RequestContext(request))

def feed(request, group_slug):
    try:
        if group_slug == 'all':
            feedgen = TopicFeedAll(group_slug, request).get_feed()
        else:
            group = BaseGroup.objects.get(slug=group_slug)
            
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
    
    if (request.method == "POST" and (request.user == topic.creator or topic.group.user_is_admin(request.user))):
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

def adminovision_toggle(request, group_slug=None):
    """
    Toggles admin-o-vision for the current user.
    No effect if user is not an admin
    """

    if user_can_adminovision(request.user):
        profile = request.user.get_profile()
    
        profile.adminovision = not profile.adminovision
        profile.save()
    
    # this redirect should be OK, since the adminovision link is only visible from reverse('home')
    return HttpResponseRedirect(reverse('home'))

    
