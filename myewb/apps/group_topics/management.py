"""myEWB topics management

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from permissions.models import PermissionGroup
from group_topics import models as gt
from group_topics.models import GroupTopic

def create_perm_group(sender, **kwargs):
    group, created = PermissionGroup.objects.get_or_create(name="Posts admin",
                                                           description="Full control over posts (does not affect group-based visibility though)")
    if created:
        # print 'creating topics permission group'
    
        grouptopic = ContentType.objects.get_for_model(GroupTopic)
        perm, created = Permission.objects.get_or_create(name="Posts admin",
                                                         content_type=grouptopic,
                                                         codename="admin")
        group.permissions.add(perm)
signals.post_syncdb.connect(create_perm_group, sender=gt)
