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
from conference import models as cr
from conference.models import ConferenceRegistration

def create_perm_group(sender, **kwargs):
    group, created = PermissionGroup.objects.get_or_create(name="Conference registration admin",
                                                           description="Full control over conference registration")
    if created:
        # print 'creating profiles permission group'
    
        confreg = ContentType.objects.get_for_model(ConferenceRegistration)
        perm, created = Permission.objects.get_or_create(name="Conference registration admin",
                                                         content_type=confreg,
                                                         codename="admin")
        group.permissions.add(perm)
signals.post_syncdb.connect(create_perm_group, sender=cr)
