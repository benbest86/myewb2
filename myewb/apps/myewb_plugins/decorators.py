from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from myewb_plugins.models import GroupPluginAppPreference, GroupPluginPreference, UserPluginAppPreference 
from base_groups.models import BaseGroup
class if_enabled_for_group(object):
    """
    Check to see whether a plugin is enabled for a group.
    """
    def __init__(self, app_name):
        self.app_name = app_name
    def __call__(self, f):
        def newf(request, *args, **kwargs):
            group = kwargs.get('group', None)
            if group is None:
                # custom manager method get_from_view_args is required!!
                group_slug = kwargs.get('group_slug', None)
                group = get_object_or_404(BaseGroup, slug=group_slug)
            pref = None
            try:
                pref = GroupPluginAppPreference.objects.get(group=group, plugin_app__app_name=self.app_name)
            except GroupPluginAppPreference.DoesNotExist:
                pass
            if pref:
                # add group to list of kwargs because we had to hit
                # the database to get it - no point in doing that
                # again in the view function
                kwargs['group'] = group
                return f(request, *args, **kwargs)
            else:
                # deny access
                return render_to_response('myewb_plugins/disabled.html', 
                        {'app_name': self.app_name}, 
                        context_instance=RequestContext(request))
        return newf

class if_enabled_for_user(object):
    """
    Check to see whether a plugin is enabled for a group.
    """
    def __init__(self, app_name):
        self.app_name = app_name
    def __call__(self, f):
        def newf(request, *args, **kwargs):
            user = request.user
            pref = None
            try:
                pref = UserPluginAppPreference.objects.get(user=user, plugin_app__app_name=self.app_name)
            except UserPluginAppPreference.DoesNotExist:
                pass
            if pref:
                return f(request, *args, **kwargs)
            else:
                # deny access
                return render_to_response('myewb_plugins/disabled.html', 
                        {'app_name': self.app_name}, 
                        context_instance=RequestContext(request))
        return newf
