"""myEWB GroupTopics views

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Created on: 2009-08-13
Last modified: 2009-08-15
@author: Joshua Gorner, Francis Kung
"""

from django.http import HttpResponse, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _
from django.contrib.syndication import feeds

from groups import bridge

from base_groups.models import BaseGroup
from group_topics.models import GroupTopic
from group_topics.forms import GroupTopicForm
from group_topics.feeds import TopicFeedAll, TopicFeedGroup

from attachments.forms import AttachmentForm
from attachments.models import Attachment

from topics.views import *
from topics.views import topics as pinaxtopics, topic as pinaxtopic

# FIXME: this method is copied wholesale from pinax.apps.topics.views except for one line =(

def topic(request, topic_id, group_slug=None, edit=False, template_name="topics/topic.html", bridge=None):

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
        # this is the only different line.  which is needed to keep things sane.
        topics = Topic.objects.all()
        #topics = Topic.objects.filter(object_id=None)

    topic = get_object_or_404(topics, id=topic_id)

    if (request.method == "POST" and edit == True and (request.user == topic.creator or request.user == topic.group.creator)):
        topic.body = request.POST["body"]
        topic.save()
        return HttpResponseRedirect(topic.get_absolute_url(group))

    if group:
        group_base = bridge.group_base_template()
    else:
        group_base = None

    return render_to_response(template_name, {
        "topic": topic,
        "edit": edit,
        "group": group,
        "group_base": group_base,
    }, context_instance=RequestContext(request))

def topics(request, group_slug=None, form_class=GroupTopicForm, attach_form_class=AttachmentForm, template_name="topics/topics.html", bridge=None):
    
    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    if not request.user.is_authenticated():
        is_member = False
    else:
        if group:
            is_member = group.user_is_member(request.user)
        else:
            is_member = True
    
    if group:
        group_base = bridge.group_base_template()
    else:
        group_base = None
    
    attach_count = 0
    if request.method == "POST":
        try:
            attach_count = int(request.POST["attach_count"])
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
                    base_topic = Topic.objects.get(id=topic.id)
                    for af in attach_forms:
                        attachment = af.save(request, base_topic)
                        
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
        topic_form = form_class(instance=Topic())
        attach_forms = []
    
    if group:
        topics = group.content_objects(GroupTopic)
    else:
        topics = GroupTopic.objects.all()
    
    return render_to_response(template_name, {
        "group": group,
        "topic_form": topic_form,
        "attach_forms": attach_forms,
        "attach_count": attach_count,
        "is_member": is_member,
        "topics": topics,
        "group_base": group_base,
    }, context_instance=RequestContext(request))

def feed(request, group_slug):
    try:
        if group_slug == 'all':
            feedgen = TopicFeedAll(group_slug, request).get_feed()
        else:
            group = BaseGroup.objects.get(slug=group_slug)
            if group.visibility == 'E' or (request.user.is_authenticated() and group.user_is_member(request.user)):
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
