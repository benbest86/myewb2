from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


URGENCY_CHOICES = (('critical', 'Critical'),
                   ('important', 'Important'),
                   ('normal', 'Normal'),
                   ('low', 'Low'))

TIME_CHOICES = (('a', 'Under 1 hour per week'),
                ('b', '1 - 2 hours per week'),
                ('c', '2 - 5 hours per week'),
                ('d', '5 - 10 hours per week'),
                ('e', '10+ hours per week')) 


class JobPostingManager(models.Manager):
    pass
    
class JobPosting(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(User)
    
    posted_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    deadline = models.DateField(blank=True, null=True)

    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES)
    skills = models.ManyToManyField('jobboard.Skill')
    time_required = models.CharField(max_length=10, choices=TIME_CHOICES)
    
    active = models.BooleanField(default=True)
    
    accepted_users = models.ManyToManyField(User, related_name='accepted_jobs')
    bid_users = models.ManyToManyField(User, related_name='bid_jobs')
    following_users = models.ManyToManyField(User, related_name='following_jobs')
    
    objects = JobPostingManager()

class Skill(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    