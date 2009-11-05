"""myEWB profile admin declarations

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on 2009-06-19
Last modified on 2009-07-01
@author Joshua Gorner
"""
from django.contrib import admin
from profiles.models import *

# can be further customized later if necessary

admin.site.register(Profile)
admin.site.register(MemberProfile)
admin.site.register(StudentRecord)
admin.site.register(WorkRecord)

admin.site.register(Passport)
admin.site.register(OnlineService)
admin.site.register(WebPage)
