"""myEWB stats module

This file is part of myEWB
Copyright 2010 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

@author Francis Kung
"""

from datetime import date, datetime, timedelta
from exceptions import ValueError
from django.db import models
from django.contrib.auth.models import User
from profiles.models import MemberProfile
from group_topics.models import GroupTopic
from threadedcomments.models import ThreadedComment

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
    activityCreations = models.IntegerField(default=0)
    activityEdits = models.IntegerField(default=0)
    activityConfirmations = models.IntegerField(default=0)
    activityDeletions = models.IntegerField(default=0)
    reflections = models.IntegerField(default=0)
    filesAdded = models.IntegerField(default=0)
    
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

# will be interesting to segment further: people who reply a lot but don't 
# post often? people who email a lot but rarely do front-page posts? people 
# who use champ, events, etc, a lot but rarely post,etc?
USAGE_PROFILES = ('Power user',         # lots of logins and posts
                  'Medium user',        # some logins / posts
                  'Occasional user',    # a few logins / posts
                  'Observer',           # some logins but few posts
                  'Rare user',          # few logins
                  #'Past user',          # used to use myewb, but is now a rare/inactive user
                  'New user',           # too new, no data...
                  'Inactive',           # basically never uses myewb
                  )
def usage_profile(user):
    if not user.is_authenticated() or not user.is_active:
        return False
    
    created = user.date_joined
    days_active = datetime.now() - created 
    
    if days_active.days < 14:
        return 'New user'
    
    logins = user.get_profile().login_count
    last_login = user.get_profile().current_login
    post_count = GroupTopic.objects.get_for_user(user).count()
    post_count += ThreadedComment.objects.filter(user=user).count()
    
    days_per_login = days_active.days / logins
    days_per_post = days_active.days / post_count
    
    #print "logins", logins, "active", days_active.days, "post_count", post_count, "last_login", last_login
    #print "days_per_login", days_per_login, "days_per_post", days_per_post
    
    if datetime.now() - last_login > timedelta(days=180):
        return 'Inactive'
    
    if days_per_login < 4 and days_per_post < 7:
        return 'Power user'
    
    if days_per_login < 7 and days_per_post < 14:
        return 'Medium user'
        
    if days_per_login < 14 and days_per_post < 31:
        return 'Occasional user'
    
    if days_per_login < 14:
        return 'Observer'
    
    return 'Rare user'
