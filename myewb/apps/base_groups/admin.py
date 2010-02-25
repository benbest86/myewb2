"""myEWB base groups admin declarations

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Last modified on 2009-07-29
@author Joshua Gorner
"""
from django.contrib import admin
from base_groups.models import BaseGroup, GroupMember, InvitationToJoinGroup

class BaseGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'creator', 'created')
    
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'is_admin', 'admin_title', 'joined')

class InvitationToJoinGroupAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'request_date', 'message')

admin.site.register(BaseGroup, BaseGroupAdmin)
admin.site.register(GroupMember, GroupMemberAdmin)
admin.site.register(InvitationToJoinGroup, InvitationToJoinGroupAdmin)