"""myEWB communities models declarations

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Created on 2009-07-30
@author Joshua Gorner, Benjamin Best
"""
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save
from base_groups.models import BaseGroup, GroupMember, add_creator_to_group

class Community(BaseGroup):
    def get_absolute_url(self):
        return reverse('community_detail', kwargs={'group_slug': self.slug})
       
    def save(self, force_insert=False, force_update=False):
        self.model = "Community"
        return super(Community, self).save(force_insert, force_update)
        
    class Meta:
        verbose_name_plural = "communities"
# use same add_creator_to_group from base_groups
post_save.connect(add_creator_to_group, sender=Community)
