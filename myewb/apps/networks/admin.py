from django.contrib import admin
from networks.models import Network, NetworkMember

class NetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'creator', 'created')
    
class NetworkMemberAdmin(admin.ModelAdmin):
    lsit_display = ('group', 'user', 'is_admin', 'admin_title', 'created')

admin.site.register(Network, NetworkAdmin)
admin.site.register(NetworkMember, NetworkMemberAdmin)