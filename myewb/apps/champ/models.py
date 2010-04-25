"""myEWB CHAMP models

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from base_groups.models import BaseGroup

ALLMETRICS = {'func': "Chapter Functioning",
              'ml': "Member Learning",
              'so': "School Outreach",
              'pe': "Public Outreach",
              'pa': "Advocacy",
              'wo': "Workplace Outreach",
              'ce': "Curriculum Enhancement",
              'pub': "Publicity",
              'fund': "Fundraising"}

class Activity(models.Model):
    name = models.CharField(_('Event name'), max_length=255)
    
    date = models.DateField(null=True, blank=True)
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
    
    def get_metrics(self):
        """
        Returns a list of all metrics associated with this activity,
        using the proper Metrics subclasses
        """
        results = []
        metrics = Metrics.objects.filter(activity=self.pk)
        for m in metrics:
            results.append(m.getattr(m, m.metric_type))
            
        return results
    
    def can_be_confirmed(self):
        metrics = self.get_metrics()
        for m in metrics:
            if m.can_be_confirmed() == False:
                return False
        return True
    
class Metrics(models.Model):
#    activity_id = models.PositiveIntegerField()    # don't use ForeignKey so that subclassing won't cause reverse name problems.
    activity = models.ForeignKey(Activity, related_name="%s" % __name__)
    metric_type = models.CharField(max_length=255, null=True)
    
    def __init__(self, *args, **kwargs):
        super(Metrics, self).__init__(*args, **kwargs)
        
        # want to set the type when creating the object, but not when instantiating
        # one from the database.  I probably coudl've done this by overriding 
        # save() instead... but this also works.
        if self.metric_type is None:
            self.metric_type = self.__class__.__name__.lower()
    
    def get_values(self):
        """
        Returns a subset of this metric's fields as a dict
        (removes all non-data fields)
        """
        # so awesome.
        # http://yuji.wordpress.com/2008/05/14/django-list-all-fields-in-an-object/
        fields = {}
        for f in self._meta.fields:
            fields[f.name] = getattr(self, f)
            
        if 'id' in fields:
            del fields['id']
        if 'activity_id' in fields:
            del fields['activity_id']
        if 'metric_type' in fields:
            del fields['metric_type']
        if 'metrics_ptr' in fields:
            del fields['metrics_ptr']
        if 'name' in fields:
            del fields['name']
            
        return fields
        
    def can_be_confirmed(self):
        """
        An activity can be confirmed if the metrics are all filled out...
        """
        fields = self.get_values()
        for f, value in fields:
            if value == None:
                return False
        return True
        
class MemberLearningMetrics(Metrics):
    metricname = "Member Learning"
    type = models.CharField(max_length=255, null=True, blank=True)
    learning_partner = models.BooleanField(null=True, blank=True)
    curriculum = models.CharField(max_length=255, null=True, blank=True)
    resources_by = models.CharField(max_length=255, null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    attendance = models.IntegerField(null=True, blank=True)
    new_attendance = models.IntegerField(null=True, blank=True)
    
class SchoolOutreachMetrics(Metrics):
    metricname = "School Outreach"
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
    metricname = "Chapter Functioning"
    type = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    purpose = models.CharField(max_length=255, null=True, blank=True)
    attendance = models.IntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    
class PublicEngagementMetrics(Metrics):
    metricname = "Public Outreach"
    type = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    purpose = models.CharField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    level1 = models.IntegerField(null=True, blank=True)
    level2 = models.IntegerField(null=True, blank=True)
    level3 = models.IntegerField(null=True, blank=True)
    
class PublicAdvocacyMetrics(Metrics):
    metricname = "Advocacy"
    type = models.CharField(max_length=255, null=True, blank=True)
    units = models.IntegerField(null=True, blank=True)
    decision_maker = models.CharField(max_length=255, null=True, blank=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    ewb = models.CharField(max_length=255, null=True, blank=True)
    purpose = models.CharField(max_length=255, null=True, blank=True)
    learned = models.TextField(null=True, blank=True)
    
class PublicationMetrics(Metrics):
    metricname = "Publicity"
    outlet = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    circulation = models.IntegerField(null=True, blank=True)
    
class FundraisingMetrics(Metrics):
    metricname = "Fundraising"
    goal = models.IntegerField(null=True, blank=True)
    revenue = models.IntegerField(null=True, blank=True)
    
class WorkplaceOutreachMetrics(Metrics):
    metricname = "Workplace Outreach"
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
    metricname = "Curriculum Enhancement"
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    students = models.IntegerField(null=True, blank=True)
    hours = models.IntegerField(null=True, blank=True)
    professor = models.CharField(max_length=255, null=True, blank=True)
    ce_activity = models.CharField(max_length=255, null=True, blank=True)
