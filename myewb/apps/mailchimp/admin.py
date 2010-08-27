from django.contrib import admin
from mailchimp.models import ListEvent, GroupEvent, ProfileEvent

# can be further customized later if necessary

admin.site.register(ListEvent)
admin.site.register(GroupEvent)
admin.site.register(ProfileEvent)
