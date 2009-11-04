"""myEWB TagAlias admin

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2009-10-18
@author: Francis Kung
"""

from django.contrib import admin
from tag_app.models import TagAlias

class TagAliasAdmin(admin.ModelAdmin):
    list_display = ('alias', 'tag')

admin.site.register(TagAlias, TagAliasAdmin)
