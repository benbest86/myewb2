"""myEWB CHAMP models

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from base_groups.models import BaseGroup

class Activity(models.Model):
    name = models.CharField(_('Event name'), max_length=255)
    
    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    
    creator = models.ForeignKey(User, related_name="activities_created")
    editor = models.ForeignKey(User, related_name="activities_edited")
    group = models.ForeignKey(BaseGroup)
    
    visible = models.BooleanField(default=True)
    confirmed = models.BooleanField(default=False)
    
    prepHours = models.IntegerField(null=True, blank=True)
    execHours = models.IntegerField(null=True, blank=True)
    numVolunteers = models.IntegerField(null=True, blank=True)
    
    description = models.TextField(null=True, blank=True)
    goals = models.TextField(null=True, blank=True)
    outcome = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    changes = models.TextField(null=True, blank=True)
    
    repeat = models.BooleanField(null=True, blank=True)
    
    def can_be_confirmed(self):
        # get all metrics attached to this activity
        metrics = Metrics.objects.filter(activity_id=self.pk)
        
        for m in metrics:
            # translate generic Metric object into the correct subclass
            child_metric = getattr(m, m.metric_type)
            
            # and check if it can be confirmed
            if child_metric.can_be_confirmed() == False:
                return False
        return True
    
class Metrics(models.Model):
    activity_id = models.PositiveIntegerField()    # don't use ForeignKey so that subclassing won't cause reverse name problems.
    metric_type = models.CharField(max_length=255, null=True)
    
    def __init__(self, *args, **kwargs):
        super(Metrics, self).__init__(*args, **kwargs)
        
        # want to set the type when creating the object, but not when instantiating
        # one from the database.  I probably coudl've done this by overriding 
        # save() instead... but this also works.
        if self.metric_type is None:
            self.metric_type = self.__class__.__name__.lower()
    
    def can_be_confirmed(self):
        """
        An activity can be confirmed if the metrics are all filled out...
        """
        # so awesome.
        # http://yuji.wordpress.com/2008/05/14/django-list-all-fields-in-an-object/
        fields = [f.name for f in self._meta.fields]
        if fields.count("id"):
            fields.remove("id")
        if fields.count("activity_id"):
            fields.remove("activity_id")
        if fields.count("metric_type"):
            fields.remove("metric_type")
        if fields.count("metrics_ptr"):
            fields.remove("metrics_ptr")
        
        for f in fields:
            if getattr(self, f) == None:
                return False
        return True
        
class MemberLearningMetrics(Metrics):
    type = models.CharField(max_length=255, null=True, blank=True)
    learning_partner = models.BooleanField(null=True, blank=True)
    curriculum = models.CharField(max_length=255, null=True, blank=True)
    resources_by = models.CharField(max_length=255, null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    attendance = models.IntegerField(null=True, blank=True)
    new_attendance = models.IntegerField(null=True, blank=True)
    
class SchoolOutreachMetrics(Metrics):
    school_name = models.CharField(max_length=255, null=True, blank=True)
    school_address = models.CharField(max_length=255, null=True, blank=True)
    school_phone = models.CharField(max_length=255, null=True, blank=True)
    teacher_name = models.CharField(max_length=255, null=True, blank=True)
    teacher_email = models.EmailField(null=True, blank=True)
    teacher_phone = models.CharField(max_length=255, null=True, blank=True)
    presentations = models.IntegerField(null=True, blank=True)
    students = models.IntegerField(null=True, blank=True)
    grades = models.CharField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    workshop = models.CharField(max_length=255, null=True, blank=True)
    facilitators = models.IntegerField(null=True, blank=True)
    facilitator_names = models.CharField(max_length=255, null=True, blank=True)
    new_facilitators = models.IntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
class FunctioningMetrics(Metrics):
    type = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    purpose = models.CharField(max_length=255, null=True, blank=True)
    attendance = models.IntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    
class PublicEngagementMetrics(Metrics):
    type = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    purpose = models.CharField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    level1 = models.IntegerField(null=True, blank=True)
    level2 = models.IntegerField(null=True, blank=True)
    level3 = models.IntegerField(null=True, blank=True)
    
class PublicAdvocacyMetrics(Metrics):
    type = models.CharField(max_length=255, null=True, blank=True)
    units = models.IntegerField(null=True, blank=True)
    decision_maker = models.CharField(max_length=255, null=True, blank=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    ewb = models.CharField(max_length=255, null=True, blank=True)
    purpose = models.CharField(max_length=255, null=True, blank=True)
    learned = models.TextField(null=True, blank=True)
    
class PublicationMetrics(Metrics):
    outlet = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    circulation = models.IntegerField(null=True, blank=True)
    
class FundraisingMetrics(Metrics):
    goal = models.IntegerField(null=True, blank=True)
    revenue = models.IntegerField(null=True, blank=True)
    
class WorkplaceOutreachMetrics(Metrics):
    company = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    presenters = models.CharField(max_length=255, null=True, blank=True)
    ambassador = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    presentations = models.IntegerField(null=True, blank=True)
    attendance = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    
class CurriculumEnhancementMetrics(Metrics):
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    students = models.IntegerField(null=True, blank=True)
    hours = models.IntegerField(null=True, blank=True)
    professor = models.CharField(max_length=255, null=True, blank=True)
    activity = models.CharField(max_length=255, null=True, blank=True)
     
    