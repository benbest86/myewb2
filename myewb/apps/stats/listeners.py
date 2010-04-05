"""myEWB stats module
In here, we listen for all the signal-able events to record

This file is part of myEWB
Copyright 2010 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

@author Francis Kung
"""

from django.db.models.signals import post_save, post_delete
from account_extra.signals import signup, listsignup, signin, deletion, listupgrade
from profiles.signals import regularmember, renewal

from stats.models import record

from django.contrib.auth.models import User
from group_topics.models import GroupTopic
from events.models import Event
from threadedcomments.models import ThreadedComment
from whiteboard.models import Whiteboard

def record_signup(sender, user, **kwargs):
    record("signups")
signup.connect(record_signup)

def record_listsignup(sender, user, **kwargs):
    record("mailinglistsignups")
listsignup.connect(record_listsignup)

def record_signin(sender, user, **kwargs):
    record("signins")
signin.connect(record_signin)

def record_post(sender, instance, created, **kwargs):
    if created:
        record("posts")
post_save.connect(record_post, sender=GroupTopic)

def record_event(sender, instance, created, **kwargs):
    if created:
        record("events")
post_save.connect(record_post, sender=Event)

def record_reply(sender, instance, created, **kwargs):
    if created:
        record("replies")
post_save.connect(record_reply, sender=ThreadedComment)

def record_whiteboard(sender, instance, created, **kwargs):
    record("whiteboardEdits")
post_save.connect(record_post, sender=Whiteboard)

def record_regupgrade(sender, user, **kwargs):
    record("regupgrades")
regularmember.connect(record_regupgrade)

#def record_regdowngrade(sender, user, **kwargs):
#    record("regdowngrades")
#downgrade.connect(record_regdowngrade)

def record_deletion(sender, user, **kwargs):
    record("deletions")
deletion.connect(record_deletion)

def record_renewal(sender, user, **kwargs):
    record("renewals")
renewal.connect(record_renewal)

def record_listupgrade(sender, user, **kwargs):
    record("mailinglistupgrades")
listupgrade.connect(record_listupgrade)
