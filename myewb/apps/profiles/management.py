"""myEWB profiles management

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from base_groups import models as bg
from permissions.models import PermissionGroup
from profiles import models as pr
from profiles.models import MemberProfile

def create_perm_group(sender, **kwargs):
    group, created = PermissionGroup.objects.get_or_create(name="Profiles admin",
                                                           description="Full control over profiles (member information)")
    if created:
        # print 'creating profiles permission group'
    
        profile = ContentType.objects.get_for_model(MemberProfile)
        perm, created = Permission.objects.get_or_create(name="Profiles admin",
                                                         content_type=profile,
                                                         codename="admin")
        group.permissions.add(perm)
signals.post_syncdb.connect(create_perm_group, sender=pr)
