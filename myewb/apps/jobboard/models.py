from datetime import date, datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


URGENCY_CHOICES = {'4critical': 'Critical',
                   '3important': 'Important',
                   '2normal': 'Normal',
                   '1low': 'Low'}

TIME_CHOICES = {'a': 'Under 1 hour per week',
                'b': '1 - 2 hours per week',
                'c': '2 - 5 hours per week',
                'd': '5 - 10 hours per week',
                'e': '10+ hours per week'} 


class JobPostingManager(models.Manager):
    def open(self):
        query = self.get_query_set()
        
        query = query.filter(active=True)
        query = query.filter(Q(deadline__gt=date.today()) | Q(deadline__isnull=True))

        return query
    
    def owned_by(self, user):
        query = self.get_query_set()
        query = query.filter(owner=user, active=True)
        return query
        
    def accepted(self, user):
        query = self.get_query_set()
        query = query.filter(accepted_users=user, active=True)
        return query
        
    def bid(self, user):
        query = self.get_query_set()
        query = query.filter(bid_users=user, active=True)
        return query

    def following(self, user):
        query = self.get_query_set()
        query = query.filter(following_users=user, active=True)
        return query
    
    def closed(self, user):
        query = self.get_query_set()
        query = query.filter(owner=user, active=False)
        return query
    
class JobPosting(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(User)
    
    posted_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    deadline = models.DateField(blank=True, null=True)

    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES.items())
    skills = models.ManyToManyField('jobboard.Skill', blank=True)
    time_required = models.CharField(max_length=10, choices=TIME_CHOICES.items())
    
    active = models.BooleanField(default=True)
    
    accepted_users = models.ManyToManyField(User, related_name='accepted_jobs', blank=True)
    bid_users = models.ManyToManyField(User, related_name='bid_jobs', blank=True)
    following_users = models.ManyToManyField(User, related_name='following_jobs', blank=True)
    
    objects = JobPostingManager()
    
    class Meta:
        ordering = ['-posted_date']
    
    def __unicode__(self):
        return "%s (%s)" % (self.name, self.owner.visible_name())
    
    def urgency_verbose(self):
        return URGENCY_CHOICES[self.urgency]
    
    def time_required_verbose(self):
        return TIME_CHOICES[self.time_required]

class Skill(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    
    def __unicode__(self):
        return self.name
    