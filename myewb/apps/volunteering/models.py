from django.db import models
from django.utils.translation import ugettext_lazy as _
from pinax.apps.profiles.models import Profile
from profiles.models import MemberProfile
from siteutils.countries import CountryField, COUNTRY_MAP
from siteutils.models import ServiceProvider
from datetime import datetime

### APPLICATION SESSIONS
class Session(models.Model):
  name = models.CharField(max_length=200)
  active = models.BooleanField(default=False)
  open_date = models.DateField(null=True)
  due_date = models.DateField(null=True)
  close_date = models.DateField(null=True)
  email_sent = models.NullBooleanField(null=True)
  en_instructions = models.TextField("English instructions",
                                     null=True)
  fr_instructions = models.TextField("French instructions",
                                     null=True)
  completed_application = models.TextField("Thank you message",
                                           null=True)
  close_email = models.TextField("Session closing email",
                                 null=True)
  rejection_email = models.TextField("Rejected application email",
                                     null=True)
  
  def __unicode__(self):
    return self.name
    
  def complete_applications(self):
    return self.application_set.filter(complete=True)
    
  def draft_applications(self):
    return self.application_set.filter(complete=False)
    
  class Meta:
    ordering = ('-active', '-close_date', '-open_date')

class Question(models.Model):
  question = models.TextField()
  question_order = models.PositiveSmallIntegerField()
  session = models.ForeignKey("Session")
  
  def strid(self):
      return str(self.id)
  
  class Meta:
    ordering = ('question_order', 'session')

class EvaluationCriterion(models.Model):
  criteria = models.TextField()
  criteria_order = models.PositiveSmallIntegerField()
  column_header = models.CharField(max_length=100)
  session = models.ForeignKey("Session")
  
  class Meta:
    ordering = ('criteria_order', 'session')

class CaseStudy(models.Model):
  name = models.CharField(blank=True, max_length=100, verbose_name='Case Study')
  html = models.TextField(blank=True)
  
  def __unicode__(self):
    return self.name

  class Meta:
    verbose_name_plural = "Case Studies"
    ordering = ["name"]  
  
### APPLICATIONS
class Application(models.Model):
  en_writing = models.PositiveSmallIntegerField(_("English writing"), null=True, blank=True)
  en_reading = models.PositiveSmallIntegerField(null=True, blank=True)
  en_speaking = models.PositiveSmallIntegerField(null=True, blank=True)

  fr_writing = models.PositiveSmallIntegerField(null=True, blank=True)
  fr_reading = models.PositiveSmallIntegerField(null=True, blank=True)
  fr_speaking = models.PositiveSmallIntegerField(null=True, blank=True)
  
  schooling = models.TextField(blank=True, null=True)
  resume_text = models.TextField(blank=True, null=True)
  resume_attachment = models.FileField(upload_to="XXXX") #fixme
  references = models.TextField(blank=True, null=True)
  gpa = models.PositiveIntegerField(null=True, blank=True)
  
  profile = models.ForeignKey(MemberProfile)
  session = models.ForeignKey(Session)
  complete = models.BooleanField(default=False)
  
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  
  def __unicode__(self):
    return "%s: %s" % (self.profile.name, self.session.name)
    
  def get_answers(self):
    answers = self.answer_set.all()
    answer_list = {} 
    for a in answers:
        answer_list[a.question.id] = a.answer
    return answer_list
    
class Answer(models.Model):
  answer = models.TextField()
  application = models.ForeignKey("Application")
  question = models.ForeignKey("Question")


### EVALUATIONS
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

  application = models.OneToOneField("Application")
  #application = models.ForeignKey("Application")    # django-evolve only recognizes this
  rank = models.PositiveSmallIntegerField(blank=True, null=True)
  
  # yes/no 
  interview1 = models.BooleanField()
  interview2 = models.CharField(_('interview'), max_length=10, choices=INTERVIEW_CHOICES, null=True, blank=True)

  rejection_sent = models.BooleanField()
  offer_accepted = models.BooleanField(default=True)
  
  interview1_notes = models.TextField(blank=True, null=True)
  interview2_notes = models.TextField(blank=True, null=True)
  
  ewb_experience = models.TextField(blank=True, null=True)


  application_score = models.PositiveSmallIntegerField(blank=True, null=True)
  # interview_score = sum(interview_score_leadership, interview_score_problem_solving, _africa_ready, _interpersonal, _attitudes_personal)
  # criterion table??
  
  def total_score(self):
    score = 0
    for e in self.evaluationresponse_set.all():
        score = score + e.response
    return score
    
  def scores(self):
    scores = {}
    for e in self.evaluationresponse_set.all():
        scores[e.evaluation_criterion.id] = e.response
    return scores
    
  def comments(self):
    comments = {}
    for c in self.evaluationcomment_set.all():
        comments[c.key] = c.comment
    return comments
    
class EvaluationComment(models.Model):
  evaluation = models.ForeignKey("Evaluation")
  key = models.TextField()
  comment = models.TextField()
  

### PLACEMENT TRACKING
class Sector(models.Model):
  name = models.CharField(blank=True, max_length=100)
  abbreviation = models.CharField(blank=True, max_length=30)

  def __unicode__(self):
    return self.name

class Placement(models.Model):
  description = models.TextField()
  longterm = models.BooleanField()
  deleted = models.BooleanField(default=False)
  start_date = models.DateField(null=True)
  end_date = models.DateField(null=True)
  country = CountryField(ewb='placements')
  town = models.CharField(max_length=100)
  flight_request_made = models.BooleanField(default=True)

  sector = models.ForeignKey(Sector, null=True)
  coach = models.ForeignKey(MemberProfile, related_name='coach', null=True)
  profile = models.ForeignKey(MemberProfile, related_name='placement')
  
  def country_name(self):
    if self.country and COUNTRY_MAP.has_key(self.country):
      return COUNTRY_MAP[self.country]

    return None

  def local_phone_numbers(self):
    if self.town:
      return self.profile.phone_numbers.filter(label=self.town)
    else:
      return None
      
  def __unicode__(self):
    return "%s: %s in %s, %s (%s--%s)" % (self.profile.name, self.sector, self.town, self.country, self.start_date, self.end_date)
  
  def description(self):
    return "%s in %s, %s (%s--%s)" % (self.sector, self.town, self.country, self.start_date, self.end_date)
  
  
  @models.permalink
  def get_absolute_url(self):
    return ("volunteering.views.placement_detail", [str(self.id)]) 

class Stipend(models.Model):
  profile = models.ForeignKey(MemberProfile, verbose_name=_('profile'), related_name="stipend")
  placement = models.ForeignKey(Placement, related_name="stipend")

  responsible_person = models.ForeignKey(MemberProfile, related_name='responsible_person', null=True)
  daily_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
  adjustment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
  repatriation_paid_quarter = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
  repatriation_accrued_quarter = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
  repatriation_paid_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
  repatriation_accrued_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
  
  notes = models.TextField(blank=True, null=True)
  repatriation_notes = models.TextField(blank=True, null=True)
  
  def __unicode__(self):
    return "%s: %s, %s: %s" % (self.profile.name, self.placement.town, self.placement.country, self. daily_rate)

  def payment(self):
    return (float(self.daily_rate) * 90)

  def adjusted_payment(self):
    return (float(self.daily_rate) * 90 + float(self.adjustment))

class InsuranceInstance(models.Model):
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

  profile = models.ForeignKey(MemberProfile, related_name='travel_segment')
  placement = models.ForeignKey(Placement)

  start_date_time = models.DateTimeField(blank=True)
  end_date_time = models.DateTimeField(blank=True)
  
  # airport code
  start_location = models.CharField(blank=True, max_length=100)
  end_location = models.CharField(blank=True, max_length=100)
  
  booking_code = models.CharField(blank=True, max_length=100)
  notes = models.TextField(blank=True)
  
  payment_method = models.CharField(_('payment method'), max_length=100, choices=PAYMENT_CHOICES, null=True, blank=True)
  purpose = models.CharField(_('purpose'), max_length=100, choices=PURPOSE_CHOICES, null=True, blank=True)
  
  def __unicode__(self):
    return "%s (%s)" % (self.profile.name, self.booking_code)

class SendingGroup(models.Model):
  group_type = models.CharField(blank=True, max_length=100)
  season = models.CharField(blank=True, max_length=100)
  year = models.PositiveIntegerField()
  
  def __unicode__(self):
    return "%s %s %s" % (self.group_type, self.season, self.year)

