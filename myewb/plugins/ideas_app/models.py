from django.db import models
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

# from base_groups.models import BaseGroup

# Create your models here.

class IdeaManager(models.Manager):
    def all_time(self):
        return self.order_by('-votes')
    # XXX add more types like 'hot' here

class Idea(models.Model):
    
    # Could link group with BaseGroup as well
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    group = generic.GenericForeignKey('content_type', 'object_id')
    
    name = models.CharField(max_length=50)
    creator = models.ForeignKey(User)
    description = models.TextField()
    votes = models.IntegerField(blank=True, default=0)
    created_on = models.DateTimeField(auto_now_add=True)

    objects = IdeaManager()
    @models.permalink
    def get_absolute_url(self):
        return ('idea_detail', [str(self.id)])

class IdeaVote(models.Model):
    idea = models.ForeignKey(Idea)
    user = models.ForeignKey(User)

    class Meta:
        # users can only have one vote per idea
        unique_together = (('idea', 'user'),)

def add_vote(sender, instance, created, **kwargs):
    if instance.created:
        instance.idea.votes += 1
        instance.idea.save()

def subtract_vote(sender, instance, **kwargs):
    instance.idea.votes -= 1
    instance.idea.save()

post_save.connect(add_vote, sender=IdeaVote)
post_delete.connect(subtract_vote, sender=IdeaVote)
