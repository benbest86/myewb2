from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from myewb_plugins.models import PluginApp, UserPluginAppPreference, GroupPluginAppPreference

@login_required
def user_prefs_index(request, template_name='myewb_plugins/user_prefs.html'):
    user = request.user
    personal_plugin_apps = PluginApp.objects.filter(plugin_type='personal')
    prefs = UserPluginAppPreference.objects.filter(user=user)
    plugin_apps = {}
    for app in personal_plugin_apps:
        plugin_apps[app.app_name] = {'app':app, 'enabled':0}
    for pref in prefs:
        plugin_apps[pref.plugin_app.app_name]['enabled'] = 1
        print 'enabled for', pref.plugin_app.app_name
    plugin_apps = plugin_apps.values()
    return render_to_response(
            template_name,
            {'plugin_apps': plugin_apps},
            context_instance=RequestContext(request),
            )

@login_required
def user_pref_detail(request, plugin_app_id):
    if request.method == 'POST':
        user = request.user
        plugin_app = get_object_or_404(PluginApp, id=plugin_app_id)
        enabled = request.POST.get(plugin_app.app_name)
        if enabled:
            plugin_app.enable_for_entity(user)
        else:
            plugin_app.disable_for_entity(user)
        return HttpResponseRedirect(reverse('user_plugin_prefs_index'))

@login_required
def widget_prefs_index(request, template_name='myewb_plugins/widget_prefs.html'):
    user = request.user
    personal_plugin_apps = PluginApp.objects.filter(plugin_type='personal')
    prefs = UserPluginAppPreference.objects.filter(user=user)
    plugin_apps = {}
    for app in personal_plugin_apps:
        plugin_apps[app.app_name] = {'app':app, 'enabled':0}
    for pref in prefs:
        plugin_apps[pref.plugin_app.app_name]['enabled'] = 1
        print 'enabled for', pref.plugin_app.app_name
    plugin_apps = plugin_apps.values()
    return render_to_response(
            template_name,
            {'plugin_apps': plugin_apps},
            context_instance=RequestContext(request),
            )

@login_required
def widget_pref_detail(request, plugin_app_id):
    if request.method == 'POST':
        user = request.user
        plugin_app = get_object_or_404(PluginApp, id=plugin_app_id)
        enabled = request.POST.get(plugin_app.app_name)
        if enabled:
            plugin_app.enable_for_entity(user)
        else:
            plugin_app.disable_for_entity(user)
        return HttpResponseRedirect(reverse('user_plugin_prefs_index'))

