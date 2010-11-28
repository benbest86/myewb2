"""myEWB CHAMP models

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from base_groups.models import BaseGroup
from siteutils.shortcuts import get_object_or_none

ALLMETRICS = (('all', "Event Impact"),
              ('func', "Chapter Functioning"),
              ('ml', "Member Learning"),
              ('so', "School Outreach"),
              ('pe', "Public Outreach"),
              ('pa', "Advocacy"),
              ('wo', "Workplace Outreach"),
              ('ce', "Curriculum Enhancement"),
              ('pub', "Publicity"),
              ('fund', "Fundraising"))

class Activity(models.Model):
    name = models.CharField(_('Event name'), max_length=255)
    
    date = models.DateField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    #created_date = models.DateTimeField()
    #modified_date = models.DateTimeField()
    
    creator = models.ForeignKey(User, related_name="activities_created")
    editor = models.ForeignKey(User, related_name="activities_edited")
    group = models.ForeignKey(BaseGroup)
    
    visible = models.BooleanField(default=True)
    confirmed = models.BooleanField(default=False)
    
    prepHours = models.IntegerField(null=True, blank=True)
    execHours = models.IntegerField(null=True, blank=True)
    numVolunteers = models.IntegerField(null=True, blank=True)
    
    def get_metrics(self, pad = False):
        """
        Returns a list of all metrics associated with this activity,
        using the proper Metrics subclasses
        """
        results = []
        metrics = Metrics.objects.filter(activity=self.pk)
        
        for m in metrics:
            results.append(getattr(m, m.metric_type))
            
        # and sort the results, by the ordering in ALLMETRICS
        results2 = []
        for m, mname in ALLMETRICS:
            found = False
            for n in results:
                if m == n.metricname:
                    results2.append(n)
                    found = True
            if pad and not found:
                results2.append(None)
            
        return results2
    
    # the inverse of get_metrics: return list of all metrics that are NOT
    # associated with this activity
    def get_available_metrics(self):
        results = []
        metrics = Metrics.objects.filter(activity=self.pk)
        print "hello??"
        
        for m in metrics:
            m = getattr(m, m.metric_type)
            results.append(m.metricname)
            
        available = {}
        for m, mname in ALLMETRICS:
            if m not in results:
                available[m] = mname
                
        return available
    
    def can_be_confirmed(self):
        metrics = self.get_metrics()
        for m in metrics:
            if m.can_be_confirmed() == False:
                return False
        return True
    
class YearPlan(models.Model):
    year = models.IntegerField()
    group = models.ForeignKey(BaseGroup, unique_for_year="year")
    modified_date = models.DateTimeField(auto_now=True, editable=False)
    #modified_date = models.DateTimeField(editable=False, default=datetime.now())
    last_editor = models.ForeignKey(User)
    
    
    ml_total_hours = models.IntegerField(null=True, blank=True,  verbose_name=_('<b>Member learning:</b> Total Hours'))
    ml_average_attendance = models.IntegerField(null=True, blank=True,  verbose_name=_('<b>Member learning:</b> Average Attendance'))
    
    eng_people_reached = models.IntegerField(null=True, blank=True,  verbose_name=_('<b>Public Outreach:</b> People Reached')) # @@@ I hope this is the case! eng_people_reached != public outreach ??
    
    adv_contacts = models.IntegerField(null=True, blank=True,  verbose_name=_('<b>Advocacy:</b> Contacts with decision makers'))

    ce_hours = models.IntegerField(null=True, blank=True,  verbose_name=_('<b>Curriculum Enhancement:</b> Total Class Hours'))
    ce_students = models.IntegerField(null=True, blank=True,  verbose_name=_('<b>Curriculum Enhancement:</b> Students Reached'))

    wo_presentations = models.IntegerField(null=True, blank=True,  verbose_name=_('<b>Workplace Outreach:</b> Presentations'))
    wo_reached = models.IntegerField(null=True, blank=True,  verbose_name=_('<b>Workplace Outreach:</b> Professionals Reached'))

    so_presentations = models.IntegerField(null=True, blank=True,  verbose_name=_('<b>School Outreach:</b> Presentations'))
    so_reached = models.IntegerField(null=True, blank=True,  verbose_name=_('<b>School Outreach:</b> Students Reached'))

    fund_total = models.IntegerField(null=True, blank=True,  verbose_name=_('<b>Fundraising:</b> Dollars Fundraised'))
    
    pub_media_hits = models.IntegerField(null=True, blank=True,  verbose_name=_('<b>Publicity:</b> Media Hits'))



    
class Metrics(models.Model):
#    activity_id = models.PositiveIntegerField()    # don't use ForeignKey so that subclassing won't cause reverse name problems.
    activity = models.ForeignKey(Activity, related_name="%s" % __name__,
                                 editable=False)
    metric_type = models.CharField(max_length=255, null=True,
                                   editable=False)
    required_fields = 'all'
    
    def __init__(self, *args, **kwargs):
        super(Metrics, self).__init__(*args, **kwargs)
        
        # want to set the type when creating the object, but not when instantiating
        # one from the database.  I probably coudl've done this by overriding 
        # save() instead... but this also works.
        if self.metric_type is None:
            self.metric_type = self.__class__.__name__.lower()
    
    def get_values(self, use_verbosename=True):
        """
        Returns a subset of this metric's fields as a dict
        (removes all non-data fields)
        
        If use_verbosename=True, it'll use the verbose field name as a key instead
        of the django internal field name 
        """
        # so awesome.
        # http://yuji.wordpress.com/2008/05/14/django-list-all-fields-in-an-object/
        fields = {}
        for f in self._meta.fields:
            if f.name == 'id':
                pass
            elif f.name == 'activity_id':
                pass
            elif f.name == 'activity':
                pass
            elif f.name == 'metric_type':
                pass
            elif f.name == 'metrics_ptr':
                pass
            elif f.name == 'name':
                pass
            else:
                if use_verbosename:
                    fields[f.verbose_name] = getattr(self, f.name)
                else:
                    fields[f.name] = getattr(self, f.name)
            
        return fields
        
    def can_be_confirmed(self):
        """
        An activity can be confirmed if the metrics are all filled out...
        """
        fields = self.get_values(use_verbosename=False)
        required = self.required_fields
        
        print required
        for f, value in fields.items():
            if (value == None or value == "") and (required == 'all' or f in required):
                return False
        return True

class ImpactMetrics(Metrics):
    metricname = "all"
    required_fields = ['description', 'goals']
    
    description = models.TextField(verbose_name="Description",
                                   null=True, blank=True)
    goals = models.TextField(verbose_name="Goals",
                             null=True, blank=True)
    outcome = models.TextField(verbose_name="Outcomes",
                               null=True, blank=True)
    notes = models.TextField(verbose_name="Notes",
                             null=True, blank=True)
    changes = models.TextField(verbose_name="What changes would you make next time?",
                               null=True, blank=True)
    repeat = models.NullBooleanField(verbose_name="Would you repeat this event", blank=True)
    
class MemberLearningMetrics(Metrics):
    metricname = "ml"
    
    type = models.CharField(verbose_name="Activity Type",
                            max_length=255, null=True, blank=True)
    learning_partner = models.NullBooleanField(verbose_name="LP related?", blank=True)
    curriculum = models.CharField(verbose_name="Curriculum",
                                  max_length=255, null=True, blank=True)
    resources_by = models.CharField(verbose_name="Resources developed by",
                                    max_length=255, null=True, blank=True)
    duration = models.FloatField(verbose_name="Duration",
                                 null=True, blank=True)
    attendance = models.IntegerField(verbose_name="Attendees",
                                     null=True, blank=True)
    new_attendance = models.IntegerField(verbose_name="New Attendees",
                                         null=True, blank=True)
    
class SchoolOutreachMetrics(Metrics):
    metricname = "so"
    school_name = models.CharField(verbose_name="Name of school",
                                   max_length=255, null=True, blank=True)
    teacher_name = models.CharField(verbose_name="Teacher's name",
                                    max_length=255, null=True, blank=True)
    teacher_email = models.EmailField(verbose_name="Teacher's email",
                                      null=True, blank=True)
    teacher_phone = models.CharField(verbose_name="Teacher's phone number",
                                     max_length=255, null=True, blank=True)
    presentations = models.IntegerField(verbose_name="# of presentations",
                                        null=True, blank=True)
    students = models.IntegerField("# of students",
                                   null=True, blank=True)
    grades = models.CharField("Grades",
                              max_length=255, null=True, blank=True)
    subject = models.CharField(verbose_name="Class",
                               max_length=255, null=True, blank=True)
    workshop = models.CharField(verbose_name="Workshop",
                                max_length=255, null=True, blank=True)
    facilitators = models.IntegerField("# of facilitators",
                                       null=True, blank=True)
    new_facilitators = models.IntegerField("# of new facilitators",
                                           null=True, blank=True)
    notes = models.TextField("Notes",
                             null=True, blank=True)
    
class FunctioningMetrics(Metrics):
    metricname = "func"
    type = models.CharField(verbose_name="Event Type",
                            max_length=255, null=True, blank=True)
    location = models.CharField("Location",
                                max_length=255, null=True, blank=True)
    purpose = models.CharField("Purpose",
                               max_length=255, null=True, blank=True)
    attendance = models.IntegerField("Attendance",
                                     null=True, blank=True)
    duration = models.FloatField("Duration (hrs)",
                                 null=True, blank=True)
    
class PublicEngagementMetrics(Metrics):
    metricname = "pe"
    type = models.CharField("Event Type",
                            max_length=255, null=True, blank=True)
    location = models.CharField("Location",
                                max_length=255, null=True, blank=True)
    purpose = models.CharField("Purpose",
                               max_length=255, null=True, blank=True)
    subject = models.CharField("Subject",
                               max_length=255, null=True, blank=True)
    level1 = models.IntegerField("People reached, level 1",
                                 null=True, blank=True)
    level2 = models.IntegerField("People reached, level 2",
                                 null=True, blank=True)
    level3 = models.IntegerField("People reached, level 3",
                                 null=True, blank=True)
    
class PublicAdvocacyMetrics(Metrics):
    metricname = "pa"
    type = models.CharField(verbose_name="Event Type",
                            max_length=255, null=True, blank=True)
    units = models.IntegerField("Units",
                                null=True, blank=True)
    decision_maker = models.CharField("Decision-maker",
                                      max_length=255, null=True, blank=True)
    position = models.CharField("Position",
                                max_length=255, null=True, blank=True)
    ewb = models.CharField("EWBer who initiated",
                           max_length=255, null=True, blank=True)
    purpose = models.CharField("Purpose",
                               max_length=255, null=True, blank=True)
    learned = models.TextField("What we learned",
                               null=True, blank=True)
    
class PublicationMetrics(Metrics):
    metricname = "pub"
    outlet = models.CharField(verbose_name="Name of media outlet",
                              max_length=255, null=True, blank=True)
    type = models.CharField("Type of media",
                            max_length=255, null=True, blank=True)
    location = models.CharField("Location",
                                max_length=255, null=True, blank=True)
    circulation = models.IntegerField("Circulation/viewership",
                                      null=True, blank=True)
    
class FundraisingMetrics(Metrics):
    metricname = "fund"
    goal = models.IntegerField(verbose_name="Fundraising goal",
                               null=True, blank=True)
    revenue = models.IntegerField(verbose_name="Approximate revenue",
                                  null=True, blank=True)
    
class WorkplaceOutreachMetrics(Metrics):
    metricname = "wo"
    company = models.CharField(verbose_name="Company name",
                               max_length=255, null=True, blank=True)
    city = models.CharField(verbose_name="City",
                            max_length=255, null=True, blank=True)
    presenters = models.CharField(verbose_name="Presenters",
                                  max_length=255, null=True, blank=True)
    ambassador = models.CharField(verbose_name="Ambassador name",
                                  max_length=255, null=True, blank=True)
    email = models.EmailField(verbose_name="Ambassador email",
                              null=True, blank=True)
    phone = models.CharField(verbose_name="Ambassador phone number",
                             max_length=255, null=True, blank=True)
    presentations = models.IntegerField(verbose_name="# of presentations",
                                        null=True, blank=True)
    attendance = models.IntegerField(verbose_name="# of attendees",
                                     null=True, blank=True)
    type = models.CharField(verbose_name="Type of presentation",
                            max_length=255, null=True, blank=True)
    
class CurriculumEnhancementMetrics(Metrics):
    metricname = "ce"
    name = models.CharField(verbose_name="Course name",
                            max_length=255, null=True, blank=True)
    code = models.CharField(verbose_name="Course code",
                            max_length=255, null=True, blank=True)
    students = models.IntegerField(verbose_name="# of students reached",
                                   null=True, blank=True)
    hours = models.IntegerField(verbose_name="Total class hours",
                                null=True, blank=True)
    professor = models.CharField(verbose_name="Professor",
                                 max_length=255, null=True, blank=True)
    ce_activity = models.CharField(verbose_name="Activity",
                                   max_length=255, null=True, blank=True)

class Journal(models.Model):
    date = models.DateField(auto_now_add=True)
    creator = models.ForeignKey(User)
    group = models.ForeignKey(BaseGroup)
    private = models.BooleanField(verbose_name="Private?",
                                  help_text="checking this box means that only you and office members will be able to read this entry. Note that default is private.",
                                  default=True)

    snapshot = models.TextField(verbose_name="Chapter Pulse",
                                help_text="Please provide a quick chapter snapshot, an anecdote, a story, a rant, an observation, a hope or a fear of this month. This can be a big picture comment including both a highlight and a key challenge:",
                                null=True, blank=True)
    highlight = models.TextField(verbose_name="Team Health: Think, Do, Love",
                                 help_text="Please share a highlight of how your team is doing",
                                 null=True, blank=True)
    challenge = models.TextField(verbose_name="",
                                 help_text="Please share a key challenge of how your team is doing:",
                                 null=True, blank=True)
    leadership = models.TextField(verbose_name="Culture Check: Leadership, Learning, Innovation",
                                  help_text="Please comment on the presence/development of leadership at your chapter:",
                                  null=True, blank=True)
    learning = models.TextField(verbose_name="",
                                help_text="Please comment on the presence/development of learning at your chapter:",
                                null=True, blank=True)
    innovation = models.TextField(verbose_name="",
                                  help_text="Please comment on the presence/development of innovation at your chapter:",
                                  null=True, blank=True)
    yearplan = models.TextField(verbose_name="Year Plan",
                                help_text="Please comment on what goals are being achieved and what needs more work that has not already been mentioned above. Where the goals are referring to all program areas that make up the chapter, such as Member Learning, Fundraising, or School Outreach, to name a few:",
                                null=True, blank=True)
    office = models.TextField(verbose_name="National Office",
                              help_text="Please include any questions and comments you may have for your chapter buddy or the National Office? What does the national office need to know",
                              null=True, blank=True)
    
    def get_fields(self):
        
        fields = []
        for f in self._meta.fields:
            if f.name in ('snapshot', 'highlight', 'challenge', 'leadership', 'learning', 'innovation', 'yearplan', 'office'):
                fields.append((f, getattr(self, f.name)))
                
        return fields
