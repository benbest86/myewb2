"""myEWB communities models declarations

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Created on 2009-07-30
@author Joshua Gorner, Benjamin Best
"""
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save

from base_groups.models import BaseGroup, GroupMember
from myewb_plugins.models import PluginApp, GroupPluginAppPreference

class Community(BaseGroup):
    base_group = models.OneToOneField(BaseGroup, parent_link=True)
    def get_absolute_url(self):
        return reverse('community_detail', kwargs={'group_slug': self.slug})
       
    def save(self, force_insert=False, force_update=False):
        self.model = "Community"
        return super(Community, self).save(force_insert, force_update)
        
    class Meta:
        verbose_name_plural = "communities"
        
# enables group plugin capability on this content type
def create_preferences_for_community(sender, instance, created, **kwargs):
    if created:
        for plugin_app in PluginApp.objects.filter(plugin_type='group', default_visibility=True):
            GroupPluginAppPreference.objects.create(group=instance.base_group, plugin_app=plugin_app)
post_save.connect(create_preferences_for_community, sender=Community)
