import myewb_plugins

register = myewb_plugins.Library()

def user_preferences(plugin, context, user, *args, **kwargs):
    """
    Defining the user preference page.
    """
    plugin_app = plugin.plugin_app
    enabled = UserPluginAppPreference.objects.filter(user=user, plugin_app=plugin_app).count()
    return {
            'plugin_app': plugin_app,
            'enabled': enabled,
            }
# register.plugin(takes_context=True, takes_user=True)(user_preferences)

def menu_tab(plugin, context, user, *args, **kwargs):
    return {}
register.plugin(takes_context=True, takes_user=True)(menu_tab)
