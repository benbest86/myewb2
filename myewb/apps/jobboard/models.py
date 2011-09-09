from datetime import date, datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


URGENCY_CHOICES = {'4critical': 'Critical',
                   '3important': 'Important',
                   '2normal': 'Normal',
                   '1low': 'Low'}
URGENCY_CHOICES_ITEMS = sorted(URGENCY_CHOICES.iteritems(), key=lambda item: item[0])

TIME_CHOICES = {'a': 'Under 1 hour per week',
                'b': '1 - 2 hours per week',
                'c': '2 - 5 hours per week',
                'd': '5 - 10 hours per week',
                'e': '10+ hours per week'} 
TIME_CHOICES_ITEMS = sorted(TIME_CHOICES.iteritems(), key=lambda item: item[0])


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
        query = query.filter(jobinterest__user=user, jobinterest__accepted=True, active=True)
        return query
        
    def bid(self, user):
        query = self.get_query_set()
        query = query.filter(jobinterest__user=user, jobinterest__accepted=False, active=True)
        return query

    def following(self, user):
        query = self.get_query_set()
        query = query.filter(following_users=user, active=True)
        return query
    
    def closed(self, user):
        query = self.get_query_set()
        query = query.filter(owner=user, active=False)
        return query
    
    # find all postings where user1 is the owner and user2 is interested (bid/accepted)
    def connected(self, user1, user2):
        query = self.get_query_set()
        query = query.filter(owner=user1, active=True, interested_users=user2)
        return query

class JobPosting(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(User)
    
    posted_date = models.DateTimeField(auto_now_add=True, db_index=True)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)
    deadline = models.DateField(blank=True, null=True, db_index=True)

    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES_ITEMS, db_index=True)
    skills = models.ManyToManyField('jobboard.Skill', blank=True, db_index=True)
    time_required = models.CharField(max_length=10, choices=TIME_CHOICES_ITEMS, db_index=True)
    location = models.ForeignKey('jobboard.Location', blank=True, null=True)
    
    active = models.BooleanField(default=True, db_index=True)
    
    #accepted_users = models.ManyToManyField(User, related_name='accepted_jobs', blank=True)
    interested_users = models.ManyToManyField(User, related_name='interested_jobs', blank=True, through="JobInterest")
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
    
    def accepted_users(self):
        return User.objects.filter(jobinterest__job=self, jobinterest__accepted=True)

    def bid_users(self):
        return User.objects.filter(jobinterest__job=self, jobinterest__accepted=False)

class Skill(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    
    class Meta:
        ordering = ['name']
    
    def __unicode__(self):
        return self.name
    
class Location(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    
    class Meta:
        ordering = ['name']
    
    def __unicode__(self):
        return self.name
    
class JobInterest(models.Model):
    job = models.ForeignKey(JobPosting)
    user = models.ForeignKey(User)
    accepted = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)
    
    statement = models.TextField(blank=True, null=True)

    
class JobFilter(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User)
    email = models.BooleanField(default=False)
    
    deadline = models.DateField(blank=True, null=True)
    deadline_comparison = models.CharField(max_length=10, blank=True, null=True)
    
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES.items(), blank=True, null=True)
    urgency_comparison = models.CharField(max_length=10, blank=True, null=True)
    
    skills = models.ManyToManyField('jobboard.Skill', blank=True)
    skills_comparison = models.CharField(max_length=10, blank=True, null=True)

    time_required = models.CharField(max_length=10, choices=TIME_CHOICES.items(), blank=True, null=True)
    time_required_comparison = models.CharField(max_length=10, blank=True, null=True)
    
    location = models.ManyToManyField('jobboard.Location', blank=True)
    location_comparison = models.CharField(max_length=10, blank=True, null=True)

    search = models.CharField(max_length=255, blank=True, null=True)
