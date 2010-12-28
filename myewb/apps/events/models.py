from django.db import models
from django.template.defaultfilters import slugify

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from lxml.html.clean import clean_html, autolink_html, Cleaner

from base_groups.helpers import user_can_adminovision, user_can_execovision
from base_groups.models import BaseGroup
from siteutils.helpers import wiki_convert
from whiteboard.models import Whiteboard

class EventManager(models.Manager):

    def visible(self, user=None):
        """
        Returns visible events by group visibility. Takes an optional
        user parameter which adds events from groups that the
        member is a part of. Handles AnonymousUser instances
        transparently.
        
        Disgustingly massive code re-use here, in group_topics.models.GroupTopicManager,
        and whiteboards.WhiteboardManager - should really clean this up.
        """
        filter_q = Q(parent_group__visibility='E')
        if user is not None and not user.is_anonymous():
            
            # admins with admin-o-vision on automatically see everything
            if user_can_adminovision(user) and user.get_profile().adminovision == 1:
                return self.get_query_set()
            
            # and similar for exec-o-vision, except only for your own chapter's groups
            if user_can_execovision(user) and user.get_profile().adminovision == 1:
                filter_q |= Q(parent_group__parent__members__user=user,
                              parent_group__parent__members__is_admin=True)
            
            # everyone else only sees stuff from their own groups
            filter_q |= Q(parent_group__member_users=user)

        # would it be more efficient to remove the OR query above and just write
        # two different queries, instead of using distinct() here?
        return self.get_query_set().filter(filter_q).distinct()
    
    def get_for_group(self, group):
        """
        Returns all posts belonging to a given group
        """
        return self.get_query_set().filter(parent_group=group)
    
class Event(models.Model):
    ''' Simple event-tag with owner and content_object + meta_data '''
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, editable=False)
    
    location = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)

    start = models.DateTimeField(verbose_name="Date and Time")
    end = models.DateTimeField(verbose_name="End Date and Time")

    owner = models.ForeignKey('auth.User')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    parent_group = models.ForeignKey(BaseGroup, related_name="events", verbose_name=_('parent'), null=True)
    
    whiteboard = models.ForeignKey(Whiteboard, related_name="event", verbose_name=_('whiteboard'), null=True)
    
    converted = models.BooleanField(default=True, editable=False)
    modified_date = models.DateTimeField(auto_now=True)
    
    objects = EventManager()

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        
        # wiki parse if needed
        if self.pk and not self.converted and self.description:
            self.description = wiki_convert(self.description)
            self.converted = True
            self.save()

    def __unicode__(self):
        return "%s, %s" % (self.slug, self.start.date())

    @models.permalink
    def get_absolute_url(self):
        ''' should be /events/<id>/slug/'''
        return ('events.views.detail', (), {
                'id':str(self.id),
                'slug':self.slug
            }
        )

    def save(self, force_insert=False, force_update=False):
        ''' Automatically generate the slug from the title '''
        self.slug = slugify(self.title)
        
        # and set the parent_group property
        # (to be honest, we could probably do away with generic foreign keys altogether)
        base_group_type = ContentType.objects.get_for_model(BaseGroup)
        if self.content_type == base_group_type:
            group = BaseGroup.objects.get(id=self.object_id)
            self.parent_group = group
        else:
            self.parent_group = None
        
        # validate HTML content
        # Additional options at http://codespeak.net/lxml/lxmlhtml.html#cleaning-up-html
        if self.description:
            self.description = clean_html(self.description)
            self.description = autolink_html(self.description)
        
        super(Event, self).save(force_insert, force_update)

    class Meta:
        ordering=( '-start', )
