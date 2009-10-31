from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

class Application(models.Model):
    en_writing = models.PositiveSmallIntegerField(_("English writing (1-10)"))
    en_reading = models.PositiveSmallIntegerField()
    en_speaking = models.PositiveSmallIntegerField()

    fr_writing = models.PositiveSmallIntegerField()
    fr_reading = models.PositiveSmallIntegerField()
    fr_speaking = models.PositiveSmallIntegerField()
    
    schooling = models.TextField()
    resume = models.TextField()
    references = models.TextField()
    gpa = models.PositiveIntegerField()
    
    user = models.ForeignKey(User)
    session = models.ForeignKey("Session")

class Session(models.Model):
  name = models.CharField(max_length=200)
  en_instructions = models.TextField()
  fr_instructions = models.TextField()
  close_email = models.TextField()
  rejection_email = models.TextField()
  completed_application = models.TextField()
  open_date = models.DateField()
  close_date = models.DateField()
  due_date = models.DateField()
  email_sent = models.BooleanField()
  
class Question(models.Model):
  question = models.TextField()
  question_order = models.PositiveSmallIntegerField()
  session = models.ForeignKey("Session")

class Answer(models.Model):
  answer = models.TextField()
  application = models.ForeignKey("Application")
  question = models.ForeignKey("Question")

class Placement(models.Model):
  name = models.CharField(max_length=200)
  description = models.TextField()
  longterm = models.BooleanField()
  active = models.BooleanField(default=True)
  deleted = models.BooleanField(default=False)
  start_date = models.DateField(null=True)
  end_date = models.DateField(null=True)
  country = models.CharField(max_length=2)
  town = models.CharField(max_length=100)

  user = models.ForeignKey(User)
  
  def __unicode__(self):
    return self.name
    
  @models.permalink
  def get_absolute_url(self):
    return ("volunteering.views.placement_detail", [str(self.id)])
    

class EvaluationCriterion(models.Model):
  criteria = models.TextField()
  column_header = models.CharField(max_length=100)
  session = models.ForeignKey("Session")

class EvaluationResponse(models.Model):
  response = models.PositiveIntegerField()
  evaluation = models.ForeignKey("Evaluation")
  evaluation_criterion = models.ForeignKey("EvaluationCriterion")

class Evaluation(models.Model):
  notes = models.TextField()
  rejection_sent = models.BooleanField()
  application = models.ForeignKey("Application")

