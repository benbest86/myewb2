"""myEWB groups management (notifications)

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Last modified on 2009-07-29
@author Joshua Gorner
"""

from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
    
    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("groups_new_member", _("New Group Member"), _("a group you are a member of has a new member"), default=1)
        notification.create_notice_type("groups_created_new_member", _("New Member Of Group You Created"), _("a group you created has a new member"), default=2)
        notification.create_notice_type("groups_new_group", _("New Group Created"), _("a new group has been created"), default=1)
        
    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"
