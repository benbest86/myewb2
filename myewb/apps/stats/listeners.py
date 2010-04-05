"""myEWB stats module
In here, we listen for all the signal-able events to record

This file is part of myEWB
Copyright 2010 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

@author Francis Kung
"""

from django.db.models.signals import post_save, post_delete

from stats.models import record

from django.contrib.auth.models import User
from group_topics.models import GroupTopic
from events.models import Event
from threadedcomments.models import ThreadedComment
from whiteboards.models import Whiteboard

def record_signup(sender, instance, created, **kwargs):
    if created:
        if instance.is_bulk:
            record("mailinglistsignups")
        else:
            record("signups")
post_save.connect(record_signup, sender=User)

def record_signin(sender, user, **kwargs):
    record("signins")

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

def record_deletion(sender, instance, **kwargs):
    record("deletions")

"""
    signins = models.IntegerField(default=0)
    eventMailings = models.IntegerField(default=0)
    regupgrades = models.IntegerField(default=0)
    regdowngrades = models.IntegerField(default=0)
    deletions = models.IntegerField(default=0)
    renewals = models.IntegerField(default=0)
    mailinglistupgrades = models.IntegerField(default=0)
"""