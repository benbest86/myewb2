"""myEWB base groups admin declarations

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Last modified on 2009-07-29
@author Joshua Gorner
"""

from django.contrib import admin
from networks.models import Network, EmailForward

class NetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'creator', 'created')
    
class EmailForwardAdmin(admin.ModelAdmin):
    list_display = ('network', 'user', 'address')

admin.site.register(Network, NetworkAdmin)
admin.site.register(EmailForward, EmailForwardAdmin)
