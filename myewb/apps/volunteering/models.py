from django.db import models

class Application(models.Model):
    en_writing = models.PositiveSmallIntegerField()
    en_reading = models.PositiveSmallIntegerField()
    en_speaking = models.PositiveSmallIntegerField()

    fr_writing = models.PositiveSmallIntegerField()
    fr_reading = models.PositiveSmallIntegerField()
    fr_speaking = models.PositiveSmallIntegerField()
    
    schooling = models.TextField()
    resume = models.TextField()
    references = models.TextField()
    gpa = models.PositiveIntegerField()
    
    user = models.ForeignKey("User")
    session = models.ForeignKey("Session")

class Session(models.Model):
  name = models.CharField()
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
  question_order = models.SmallPositiveIntegerField()
  session = models.ForeignKey("Session")

class Answer(models.Model):
  answer = models.CharField()
  application = models.ForeignKey("Application")
  question = models.ForeignKey("Question")

class Placement(models.Model):
  name = models.CharField()
  description = models.TextField()
  longterm = models.BooleanField()
  active = models.BooleanField()
  deleted = models.BooleanField()
  start_date = models.DateField()
  end_date = models.DateField()
  country = models.CharField(max_length=2)
  town = models.CharField(max_length=100)

  accounting = models.ForeignKey("Accounting")
  user = models.ForeignKey("User")

class EvaluaionCriterion(models.Model):
  criteria = models.TextField(blank=True)
  column_header = models.CharField(blank=True, max_length=100)
  session = models.ForeignKey("Session")

class EvaluationResponse(models.Model):
  response = models.PositiveIntegerField()
  evaluation = models.ForeignKey("Evaluation")
  evaluation_criteria = models.ForeignKey("EvaluationCriteria")

class Evaluation(models.Model):
  notes = models.TextField(blank=True)
  rejection_sent = models.BooleanField(default=True)
  application = models.ForeignKey("Application")
