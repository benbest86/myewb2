"""myEWB conference registration management

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
from volunteering import models as vm
from volunteering.models import Application

def create_perm_group(sender, **kwargs):
    group, created = PermissionGroup.objects.get_or_create(name="Applications admin",
                                                           description="View all applications, evaluate them, and add/edit/close application sessions")
    if created:
        # print 'creating profiles permission group'
    
        appl = ContentType.objects.get_for_model(Application)
        perm, created = Permission.objects.get_or_create(name="Applications admin",
                                                         content_type=appl,
                                                         codename="admin")
        group.permissions.add(perm)
signals.post_syncdb.connect(create_perm_group, sender=vm)
