"""myEWB communities admin declarations

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on 2009-07-30
@author Joshua Gorner
"""

from django.contrib import admin
from communities.models import Community, CommunityMember

class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'creator', 'created')
    
class CommunityMemberAdmin(admin.ModelAdmin):
    lsit_display = ('group', 'user', 'is_admin', 'admin_title', 'created')

admin.site.register(Community, CommunityAdmin)
admin.site.register(CommunityMember, CommunityMemberAdmin)