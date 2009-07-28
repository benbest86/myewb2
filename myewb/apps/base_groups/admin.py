from django.contrib import admin
from base_groups.models import BaseGroup

class BaseGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'creator', 'created')

admin.site.register(BaseGroup, BaseGroupAdmin)