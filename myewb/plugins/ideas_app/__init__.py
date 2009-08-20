import myewb_plugins
from myewb_plugins.models import PluginApp, GroupPluginAppPreference

register = myewb_plugins.Library()

def menu_tab(point, context, user, *args, **kwargs):
    """
    Adding a tab to the main menu.
    """
    return {}

# register.plugin(takes_context=True, takes_user=True)(menu_tab)

def group_plugin_menu(plugin, context, user, *args, **kwargs):
    """
    Adding in the ideas link to the group menu.
    """
    group = kwargs.get('group', None)
    if group is None:
        pass
    return {}

register.plugin(takes_context=True, takes_user=True)(group_plugin_menu)

def group_preferences(point, context, user, *args, **kwargs):
    ideas_app = PluginApp.objects.get(app_name='ideas_app')
    group = context.get('group', None)
    enabled = None
    if group:
        enabled = GroupPluginAppPreference.objects.filter(group=group, plugin_app=ideas_app).count()
    return {
            'plugin_app': ideas_app,
            'enabled': enabled,
            }
register.plugin_point(takes_context=True, takes_user=True)(group_preferences)
