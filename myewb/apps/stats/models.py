"""myEWB stats module

This file is part of myEWB
Copyright 2010 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

@author Francis Kung
"""

from datetime import date
from exceptions import ValueError
from django.db import models
from django.contrib.auth.models import User
from profiles.models import MemberProfile

class DailyStats(models.Model):
    day = models.DateField(db_index=True)
    signups = models.IntegerField(default=0)
    mailinglistsignups = models.IntegerField(default=0)
    signins = models.IntegerField(default=0)
    posts = models.IntegerField(default=0)
    events = models.IntegerField(default=0)
    eventMailings = models.IntegerField(default=0)
    replies = models.IntegerField(default=0)
    whiteboardEdits = models.IntegerField(default=0)
    regupgrades = models.IntegerField(default=0)
    regdowngrades = models.IntegerField(default=0)
    deletions = models.IntegerField(default=0)
    renewals = models.IntegerField(default=0)
    mailinglistupgrades = models.IntegerField(default=0)
    users = models.IntegerField(default=0)
    regularmembers = models.IntegerField(default=0)
    associatemembers = models.IntegerField(default=0)
    
def record(action):
    stats, created = DailyStats.objects.get_or_create(day=date.today())
    if created:
        stats.day = date.today()
        stats.users = User.objects.filter(is_active=True).count()
        stats.regularmembers = MemberProfile.objects.filter(membership_expiry__gt=date.today()).count()
        stats.associatemembers = User.objects.filter(is_active=True, is_bulk=False).count() - stats.regularmembers
    
    # so awesome.
    # http://yuji.wordpress.com/2008/05/14/django-list-all-fields-in-an-object/
    fields = [f.name for f in stats._meta.fields]
    fields.remove("id")
    fields.remove("day")
    
    if action in fields:
        setattr(stats, action, getattr(stats, action) + 1)
    else:
        raise ValueError()
        
    stats.save()
    
from stats.listeners import *
