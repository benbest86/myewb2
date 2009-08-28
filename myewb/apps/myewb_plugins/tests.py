from django.test import TestCase
from myewb_plugins.models import Widget, Plugin, PluginApp, PluginPoint, UserPluginAppPreference, MyEWBUserPluginPreference, \
        GroupPluginAppPreference, GroupPluginPreference, UserWidgetPreference
from myewb_plugins.helpers import register_plugin


