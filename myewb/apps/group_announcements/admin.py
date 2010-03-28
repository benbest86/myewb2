
from django.contrib import admin

from group_announcements.models import Announcement
from group_announcements.forms import AnnouncementAdminForm

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "creation_date", "members_only")
    list_filter = ("members_only",)
    form = AnnouncementAdminForm

admin.site.register(Announcement, AnnouncementAdmin)
