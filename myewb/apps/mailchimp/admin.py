from django.contrib import admin
from emailconfirmation.models import EmailAddress
from mailchimp.models import MailchimpEvent, ListEvent, GroupEvent, ProfileEvent

# can be further customized later if necessary

def display_user(obj):
    if obj.user.email:
        email = obj.user.email
    elif EmailAddress.objects.get_primary(obj.user):
        email = EmailAddress.objects.get_primary(obj.user)
    elif obj.user.emailaddress_set.count():
        email = obj.user.emailaddress_set.all()[0].email
    else:
        email = obj.email
         
    return "%s (%s)" % (obj.user.visible_name(), email)

class ListEventAdmin(admin.ModelAdmin):
    list_display = (display_user, 'subscribe', 'date')


admin.site.register(ListEvent, ListEventAdmin)
admin.site.register(GroupEvent)
admin.site.register(ProfileEvent)
