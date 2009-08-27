from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from library import get_library
import re

from base_groups.models import BaseGroup

ENABLED = 0
DISABLED = 1
REMOVED = 2

STATUS_CHOICES = (
    (ENABLED,  _('Enabled')),
    (DISABLED, _('Disabled')),
    (REMOVED,  _('Removed'))
)

PLUGIN_TYPES = (
        ('personal', 'Personal'),
        ('group', 'Group'),
        ('generic', 'Generic'),
        )

LABEL_RE = re.compile('^[a-zA-Z_][a-zA-Z_0-9.]*$')

def is_valid_label(name):
    return bool(LABEL_RE.match(name))

def construct_template_path(app, name, ext='.html'):
    if not is_valid_label(name): raise RuntimeError, u"invalid label: " + name
    if not is_valid_label(app): raise RuntimeError, u"invalid label: " + app
    return '/'.join([app.split('.')[-1], 'plugins', name.replace('.','/')])+ext

class PluginApp(models.Model):
    """
    Applications that register themselves as Plugins are added here.
    This allows auto-addition of urls for immediate plug-and-play addons.
    """
    app_name = models.CharField(max_length=50)
    plugin_type = models.CharField(max_length=12, choices=PLUGIN_TYPES)
    friendly_name = models.CharField(max_length=50, null=True)
    description = models.TextField()
    default_visibility = models.BooleanField(default=False)

    def __unicode__(self):
        return self.friendly_name or self.app_name

    def preferences_for_entity(self, entity):
            if self.plugin_type == 'group':
                return GroupPluginPreference.objects.filter(group=entity, plugin__plugin_app=self)
            elif self.plugin_type == 'personal':
                return MyEWBUserPluginPreference.objects.filter(user=entity, plugin__plugin_app=self)
            elif self.plugin_type == 'generic':
                content_type = ContenType.objects.get_for_model(entity)
                return GenericPluginPreference.objects.filter(content_type=content_type, object_id=entity.id, plugin__plugin_app=self)

    def enable_for_entity(self, entity):
        if self.plugin_type == 'group':
            GroupPluginAppPreference.objects.get_or_create(group=entity, plugin_app=self)
        elif self.plugin_type == 'personal':
            UserPluginAppPreference.objects.get_or_create(user=entity, plugin_app=self)

    def disable_for_entity(self, entity):
        if self.plugin_type == 'group':
            try:
                GroupPluginAppPreference.objects.get(group=entity, plugin_app=self).delete()
            except GroupPluginAppPreference.DoesNotExist:
                pass
        elif self.plugin_type == 'personal':
            try:
                UserPluginAppPreference.objects.get(user=entity, plugin_app=self).delete()
            except UserPluginAppPreference.DoesNotExist:
                pass

def claim_plugins(sender, instance, created, **kwargs):
    unclaimed_plugins = Plugin.objects.filter(plugin_app=None, label__contains='%s.' % instance.app_name)
    for plugin in unclaimed_plugins:
        plugin.plugin_app = instance
        plugin.save()

def create_permissions_for_app(sender, instance, created, **kwargs):
    plugins = instance.plugin_set.all()
    if instance.plugin_type == 'group':
        for group in BaseGroup.objects.all():
            instance.enable_for_entity(group)
    elif instance.plugin_type == 'personal':
        for user in User.objects.all():
            instance.enable_for_entity(user)
    # implement for generic!!! Maybe none???

def plugin_app_post_save(sender, instance, created, **kwargs):
    if created:
        claim_plugins(sender, instance, created, **kwargs)
        if instance.default_visibility == True:
            create_permissions_for_app(sender, instance, created, **kwargs)

post_save.connect(plugin_app_post_save, sender=PluginApp)

class PluginPoint(models.Model):
    label      = models.CharField(max_length=255, unique=True,
                    help_text=_("The label for the plugin point."))
    index      = models.IntegerField(default=0)

    registered = models.BooleanField(default=False,
                    help_text=_("is this a registered plugin point with a "
                                "library entry?"))
    status     = models.SmallIntegerField(choices=STATUS_CHOICES,
                                          default=ENABLED)

    class Meta:
        ordering = ('index', 'id')

    def __unicode__(self):
        return u'plugin_point:' + self.label

    @property
    def app(self):
        if not self.registered: return ''
        return self.label.rsplit('.', 1)[0]

    @property
    def name(self):
        return self.label.rsplit('.', 1)[-1]

    def get_plugins(self, user=None):
        """get all the plugins in appropriate order"""
        if self.status or user is None: return []
        upref = user.myewbuserpluginpreference_set.filter(plugin__status=ENABLED,
                plugin__point=self) #.order_by('index', 'id').select_related()
        # Do something here for required plugins? Do we want this functionality?
        plugins = [up.plugin for up in upref]
        return plugins

    def get_group_plugins(self, group=None):
        if self.status or group is None: return []
        upref = group.grouppluginpreference_set.filter(plugin__status=ENABLED,
                    plugin__point=self) #.order_by('index', 'id').select_related()
        # Do something here for required plugins? Do we want this functionality?
        plugins = [up.plugin for up in upref]
        return plugins

    def get_widget_prefs(self, user=None, location=None):
        """get all the widget preferences in order"""
        if self.status or user is None or location is None: return []
        wprefs = user.userwidgetpreference_set.filter(widget__status=ENABLED, widget__point=self, location=location)
        return wprefs



    def get_options(self):
        if not self.registered: return {}
        lib = get_library(self.app)
        call = lib.get_plugin_point_call(self.name)
        return call.options

    # __call__ not allowed
    def call(self, context, user, **args):
        if not self.registered: return {}
        lib = get_library(self.app)
        call = lib.get_plugin_point_call(self.name)
        options = call.options
        base = [self,]
        if options.get('takes_context', False):
            base.append(context)
        if options.get('takes_user', False):
            base.append(user)
        if options.get('takes_args', False):
            return call(*base, **args)
        return call(*base)

class PluginBase(models.Model):
    point = models.ForeignKey(PluginPoint)
    plugin_app = models.ForeignKey(PluginApp, blank=True, null=True)
    label = models.CharField(max_length=255, unique=True,
                    help_text=_("The label for the plugin point."))
    index = models.IntegerField(default=0)

    registered = models.BooleanField(default=False,
                    help_text=_("is this a registered plugin?"))
    status = models.SmallIntegerField(choices=STATUS_CHOICES,
                                          default=ENABLED)

    required = models.BooleanField(default=False,
                    help_text=_("users can not remove this plugin."))
    template = models.TextField(
                    help_text=_("template to load for the plugin."))

    class Meta:
        order_with_respect_to = 'point'
        ordering = ('point', 'index', 'id')
        abstract = True

    def __unicode__(self):
        return u'plugin:' + self.label

    @property
    def app(self):
        #if not self.registered: return ''
        return self.label[:-(len(self.point.label)+1)]

    @property
    def name(self):
        return self.point.label

    def get_options(self):
        if not self.registered: return {}
        lib = get_library(self.app)
        call = lib.get_plugin_call(self.name)
        return call.options

    #__call__ not allowed...
    def call(self, context, user, **args):
        if not self.registered: return {}
        lib = get_library(self.app)
        call = lib.get_plugin_call(self.name)

        options = call.options
        base = [self,]
        if options.get('takes_context', False):
            base.append(context)
        if options.get('takes_user', False):
            base.append(user)
        if options.get('takes_args', False):
            return call(*base, **args)
        return call(*base)

class Plugin(PluginBase):
    pass

class Widget(PluginBase):

    @property
    def app(self):
        #if not self.registered: return ''
        return self.label.split('.')[0]

    @property
    def name(self):
        return self.label.split('.', 1)[1]

    def call(self, context, user, content_object, **args):
        if not self.registered: return {}
        lib = get_library(self.app)
        call = lib.get_widget_call(self.name)

        options = call.options
        base = [self,]
        if options.get('takes_context', False):
            base.append(context)
        if options.get('takes_user', False):
            base.append(user)
        if options.get('takes_content_object', False):
            base.append(content_object)
        if options.get('takes_args', False):
            return call(*base, **args)
        return call(*base)

class MyEWBUserPluginPreference(models.Model):
    """
    Preference for an individual Plugin. Not an 
    entire plugin app.
    """
    user    = models.ForeignKey(User)
    plugin  = models.ForeignKey(Plugin)
    index   = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'plugin']
        order_with_respect_to = 'plugin'
        ordering = ('plugin', 'user', 'index', 'id')

    def __unicode__(self):
        return u':'.join(['pluginpref', self.user.username, self.plugin.label])

class UserWidgetPreference(models.Model):
    user    = models.ForeignKey(User)
    widget  = models.ForeignKey(Widget)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    location = models.CharField(max_length=250)
    index   = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'widget', 'location']
        order_with_respect_to = 'widget'
        ordering = ('widget', 'user', 'index', 'id')

    def __unicode__(self):
        return u':'.join(['pluginpref', self.user.username, self.widget.label])

class UserPluginAppPreference(models.Model):
    """
    Preference for an entire plugin app.
    """
    user    = models.ForeignKey(User)
    plugin_app  = models.ForeignKey(PluginApp)
    index   = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'plugin_app']
        order_with_respect_to = 'plugin_app'
        ordering = ('plugin_app', 'user', 'index', 'id')

    def __unicode__(self):
        return u':'.join(['plugappinpref', self.user.username, self.plugin_app.app_name])

def create_user_plugin_preferences(sender, instance, created, *args, **kwargs):
    if created:
        for plugin in instance.plugin_app.plugin_set.all():
            user_pref, created = MyEWBUserPluginPreference.objects.get_or_create(
                    user=instance.user,
                    plugin=plugin,
                    )
post_save.connect(create_user_plugin_preferences, sender=UserPluginAppPreference)

def delete_user_plugin_preferences(sender, instance, *args, **kwargs):
    prefs = MyEWBUserPluginPreference.objects.filter(
            plugin__plugin_app=instance.plugin_app, 
            user=instance.user)
    prefs.delete()
post_delete.connect(delete_user_plugin_preferences, sender=UserPluginAppPreference)

class GroupPluginPreference(models.Model):
    """
    Preference for an entire plugin app.
    """
    group = models.ForeignKey(BaseGroup)

    plugin  = models.ForeignKey(Plugin)
    index   = models.IntegerField(default=0)

    class Meta:
        unique_together = (('group', 'plugin'),)
        order_with_respect_to = 'plugin'
        ordering = ('plugin', 'group', 'index', 'id')

    def __unicode__(self):
        return u':'.join(['pluginpref', self.group.slug, str(self.plugin)])


class GroupPluginAppPreference(models.Model):
    group = models.ForeignKey(BaseGroup)

    plugin_app  = models.ForeignKey(PluginApp)
    index   = models.IntegerField(default=0)

    class Meta:
        unique_together = (('group', 'plugin_app'),)
        order_with_respect_to = 'plugin_app'
        ordering = ('plugin_app', 'group', 'index', 'id')

    def __unicode__(self):
        return u':'.join(['pluginapppref', self.group.slug, str(self.plugin_app)])

def create_group_plugin_preferences(sender, instance, created, *args, **kwargs):
    if created:
        print 'CREATING GROUP PLUGIN PREFERENCES'
        for plugin in instance.plugin_app.plugin_set.all():
            group_pref, created = GroupPluginPreference.objects.get_or_create(
                    group=instance.group,
                    plugin=plugin,
                    )
post_save.connect(create_group_plugin_preferences, sender=GroupPluginAppPreference)

def delete_group_plugin_preferences(sender, instance, *args, **kwargs):
    prefs = GroupPluginPreference.objects.filter(
            group=instance.group, 
            plugin__plugin_app=instance.plugin_app)
    prefs.delete()
post_delete.connect(delete_group_plugin_preferences, sender=GroupPluginAppPreference)

class GenericPluginPreference(models.Model):

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    plugin  = models.ForeignKey(Plugin)
    index   = models.IntegerField(default=0)

    class Meta:
        unique_together = (('object_id', 'content_type', 'plugin'),)
        order_with_respect_to = 'plugin'
        ordering = ('plugin', 'content_type', 'object_id', 'index', 'id')

    def __unicode__(self):
        return u':'.join(['pluginpref', self.content_object, self.plugin.label])

# Some other handlers to deal with user preferences

def create_preferences_for_user(sender, instance, created, **kwargs):
    if created:
        for plugin_app in PluginApp.objects.filter(plugin_type='personal', default_visibility=True):
            UserPluginAppPreference.objects.create(user=instance, plugin_app=plugin_app)
post_save.connect(create_preferences_for_user, sender=User)

# Group preference behaviour has to be dealt with in individual models.py for Group 
# content types since Sublcasses do not emit Superclass signals in Django :(
# See http://code.djangoproject.com/ticket/9318
# Currently in newtorks.models and communities.models as far as I know
