from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from siteutils.countries import CountryField
from siteutils.models import ServiceProvider
from datetime import datetime

class Application(models.Model):
  en_writing = models.PositiveSmallIntegerField(_("English writing (1-10)"))
  en_reading = models.PositiveSmallIntegerField()
  en_speaking = models.PositiveSmallIntegerField()

  fr_writing = models.PositiveSmallIntegerField()
  fr_reading = models.PositiveSmallIntegerField()
  fr_speaking = models.PositiveSmallIntegerField()
  
  schooling = models.TextField()
  resume_text = models.TextField()
  resume_attachment = models.FileField(upload_to="XXXX") #fixme
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

class Sector(models.Model):
  name = models.CharField(blank=True, max_length=100)

  def __unicode__(self):
    return self.name


class Placement(models.Model):
  name = models.CharField(max_length=200)
  description = models.TextField()
  longterm = models.BooleanField()
  deleted = models.BooleanField(default=False)
  start_date = models.DateField(null=True)
  end_date = models.DateField(null=True)
  country = CountryField(ewb='placements')
  town = models.CharField(max_length=100)
  flight_request_made = models.BooleanField(default=True)

  sector = models.ForeignKey(Sector)
  coach = models.ForeignKey(User, related_name=_('coach'))
  user = models.ForeignKey(User, null=True, related_name=_('user'))
  
  def __unicode__(self):
    return self.name
    
  @models.permalink
  def get_absolute_url(self):
    return ("volunteering.views.placement_detail", [str(self.id)]) 

class Stipend(models.Model):
  user = models.ForeignKey(User, verbose_name=_('user'))
  placement = models.ForeignKey(Placement)

  responsible_person = models.ForeignKey(User, related_name=_('responsible_person'))
  daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
  adjustment = models.DecimalField(max_digits=10, decimal_places=2)
  repatriation_amount = models.DecimalField(max_digits=10, decimal_places=2)
  
  notes = models.TextField(blank=True)
  repatriation_notes = models.TextField(blank=True)
  

class EvaluationCriterion(models.Model):
  criteria = models.TextField()
  column_header = models.CharField(max_length=100)
  session = models.ForeignKey("Session")

class EvaluationResponse(models.Model):
  response = models.PositiveIntegerField()
  evaluation = models.ForeignKey("Evaluation")
  evaluation_criterion = models.ForeignKey("EvaluationCriterion")

class Evaluation(models.Model):
  INTERVIEW_CHOICES = (
      ('Y', _('Yes')),
      ('N', _('No')),
      ('N/A', _('Not needed (hire)')),
  )

  application = models.ForeignKey("Application")
  rank = models.PositiveSmallIntegerField()
  
  # yes/no 
  interview1 = models.BooleanField()
  interview2 = models.CharField(_('interview'), max_length=10, choices=INTERVIEW_CHOICES, null=True, blank=True)

  rejection_sent = models.BooleanField()
  offer_accepted = models.BooleanField(default=True)
  
  interview1_notes = models.TextField(blank=True)
  interview2_notes = models.TextField(blank=True)
  
  ewb_experience = models.TextField(blank=True)


  application_score = models.PositiveSmallIntegerField()
  # interview_score = sum(interview_score_leadership, interview_score_problem_solving, _africa_ready, _interpersonal, _attitudes_personal)
  # criterion table??
  
  


class InsuranceInstance(models.Model):
  user = models.ForeignKey(User, verbose_name=_('user'))
  placement = models.ForeignKey(Placement)

  insurance_company = models.ForeignKey(ServiceProvider)
  policy_number = models.CharField(blank=True, max_length=100)
  certificate_number = models.CharField(blank=True, max_length=100)
  start_date = models.DateField(default=datetime.today)
  end_date = models.DateField(default=datetime.today)
  price = models.DecimalField(max_digits=10, decimal_places=2)

class TravelSegment(models.Model):
  PAYMENT_CHOICES = (
      ('travel-agent', _('Travel Agent')),
      ('aeroplan', _('Aeroplan')),
      ('ov-self-booking', _('OV self booking')),
  )

  PURPOSE_CHOICES = (
      ('conference', _('conference')),
      ('break', _('break')),
      ('emergency', _('Family Emergency')),
      ('learning-visit', _('Learning Visit')),
      ('begin-placement', _('Begin Placement')),
      ('end-placement', _('End Placement')),
  )

  user = models.ForeignKey(User, verbose_name=_('user'))
  placement = models.ForeignKey(Placement)

  start_date_time = models.DateTimeField(blank=True)
  end_date_time = models.DateTimeField(blank=True)
  
  # airport code
  start_location = models.CharField(blank=True, max_length=100)
  end_location = models.CharField(blank=True, max_length=100)
  
  booking_code = models.CharField(blank=True, max_length=100)
  notes = models.TextField(blank=True)
  
  payment_method = models.CharField(_('type'), max_length=100, choices=PAYMENT_CHOICES, null=True, blank=True)
  purpose = models.CharField(_('type'), max_length=100, choices=PURPOSE_CHOICES, null=True, blank=True)

class CaseStudy(models.Model):
  name = models.CharField(blank=True, max_length=100)
  html = models.TextField(blank=True)
  
