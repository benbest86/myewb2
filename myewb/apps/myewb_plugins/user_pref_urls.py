from django.conf.urls.defaults import *

urlpatterns = patterns('myewb_plugins.views',
        url(r'^$', 'user_prefs_index', name='user_plugin_prefs_index'),
        url(r'^(?P<plugin_app_id>\d+)/$', 'user_pref_detail', name='user_plugin_pref_detail'),
)
