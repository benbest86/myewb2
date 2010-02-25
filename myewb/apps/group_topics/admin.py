"""myEWB GroupTopics admin

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Created on: 2009-08-13
@author: Joshua Gorner
"""

from django.contrib import admin
from group_topics.models import GroupTopic, Watchlist

class GroupTopicAdmin(admin.ModelAdmin):
    list_display = ('title', )

admin.site.register(GroupTopic, GroupTopicAdmin)
admin.site.register(Watchlist)
