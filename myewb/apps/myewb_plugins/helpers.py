from myewb_plugins.models import PluginApp

def register_plugin(app_name, plugin_type='personal', friendly_name='', description='', default_visibility=False):
    app, created = PluginApp.objects.get_or_create(app_name=app_name, defaults={'plugin_type': plugin_type, 'friendly_name': friendly_name, 'description':description, 'default_visibility':default_visibility})
    if not created:
        app.plugin_type = plugin_type
        app.friendly_name = friendly_name
        app.description = description
        app.save()

