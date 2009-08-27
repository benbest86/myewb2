from django.contrib import admin
from myewb_plugins.models import PluginPoint, Plugin, MyEWBUserPluginPreference, PluginApp, GroupPluginPreference, GroupPluginAppPreference, UserPluginAppPreference, UserWidgetPreference, Widget
from myewb_plugins.forms import AdminPluginPointForm, AdminPluginForm

class PluginPointAdmin(admin.ModelAdmin):
    list_display = ('label', 'index', 'registered', 'status')
    list_filter = ('registered', 'status')
    form = AdminPluginPointForm

class PluginAdmin(admin.ModelAdmin):
    list_display = ('label', 'index', 'registered', 'required', 'status')
    list_filter = ('registered', 'status')
    form = AdminPluginForm

class MyEWBUserPluginPreferenceAdmin(admin.ModelAdmin):
    list_display = ('plugin', 'user', 'index',)

admin.site.register(PluginPoint, PluginPointAdmin)
admin.site.register(Plugin, PluginAdmin)
admin.site.register(Widget)
# admin.site.register(MyEWBUserPluginPreference, MyEWBUserPluginPreferenceAdmin)
admin.site.register(PluginApp)
admin.site.register(GroupPluginPreference)
admin.site.register(GroupPluginAppPreference)
admin.site.register(UserPluginAppPreference)
admin.site.register(UserWidgetPreference)

