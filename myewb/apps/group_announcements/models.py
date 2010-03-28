
from datetime import datetime

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from base_groups.models import BaseGroup, GroupMember
from lxml.html.clean import clean_html, autolink_html, Cleaner

try:
    set
except NameError:
    from sets import Set as set   # Python 2.3 fallback


class AnnouncementManager(models.Manager):
    """
    A basic manager for dealing with announcements.
    """
    def current(self, exclude=[], site_wide=False, for_members=False,
                user=None):
        """
        Fetches and returns a queryset with the current announcements. This
        method takes the following parameters:
        
        ``exclude``
            A list of IDs that should be excluded from the queryset.
        
        ``site_wide``
            A boolean flag to filter to just site wide announcements.
        
        ``for_members``
            A boolean flag to allow member only announcements to be returned
            in addition to any others.
            
        ``user``
            A User object: if provided will also show group-specific messages
            that this user should see
        """
        queryset = self.all()
        #if site_wide:
        #    queryset = queryset.filter(site_wide=True)
        if exclude:
            queryset = queryset.exclude(pk__in=exclude)
        if not for_members:
            queryset = queryset.filter(members_only=False)
        userfilter = Q(parent_group__isnull=True)
        if user:
            userfilter = userfilter | Q(parent_group__member_users=user)
        queryset = queryset.filter(userfilter)
        queryset = queryset.order_by("-creation_date")
        return queryset


class Announcement(models.Model):
    """
    A single announcment.
    """
    title = models.CharField(_("title"), max_length=50)
    content = models.TextField(_("content"))
    creator = models.ForeignKey(User, verbose_name=_("creator"))
    creation_date = models.DateTimeField(_("creation_date"), default=datetime.now)
    #site_wide = models.BooleanField(_("site wide"), default=False)
    members_only = models.BooleanField(_("members only"), default=False)
    parent_group = models.ForeignKey(BaseGroup, verbose_name=_("parent group"),
                                     null=True, blank=True)
    
    objects = AnnouncementManager()
    
    def get_absolute_url(self):
        return ("announcement_detail", [str(self.pk)])
    get_absolute_url = models.permalink(get_absolute_url)
    
    def save(self, force_insert=False, force_update=False):
        # validate HTML content
        # Additional options at http://codespeak.net/lxml/lxmlhtml.html#cleaning-up-html
        self.content = clean_html(self.content)
        #self.content = autolink_html(self.content)
        
        super(Announcement, self).save(force_insert, force_update)
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = _("announcement")
        verbose_name_plural = _("announcements")

def current_announcements_for_request(request, **kwargs):
    """
    A helper function to get the current announcements based on some data from
    the HttpRequest.
    
    If request.user is authenticated then allow the member only announcements
    to be returned.
    
    Exclude announcements that have already been viewed by the user based on
    the ``excluded_announcements`` session variable.
    """
    defaults = {}
    if request.user.is_authenticated():
        defaults["for_members"] = True
        defaults["user"] = request.user
    defaults["exclude"] = request.session.get("excluded_announcements", set())
    defaults.update(kwargs)
    return Announcement.objects.current(**defaults)
