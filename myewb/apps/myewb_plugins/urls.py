from django.conf.urls.defaults import *
from myewb_plugins.models import PluginApp

plugin_apps = PluginApp.objects.all()
urlpatterns = patterns('')
for app in plugin_apps:
    urls_path = '.'.join([app.app_name, 'urls'])
    try:
        _temp = __import__(urls_path, globals(), locals(), ['urlpatterns'], -1)
        urlpatterns += _temp.urlpatterns
    except:
        pass
