from django.contrib import admin
from siteutils.models import Address, PhoneNumber, ServiceProvider

admin.site.register(Address)
admin.site.register(ServiceProvider)
admin.site.register(PhoneNumber)


