from django.db import models
from django.utils.translation import ugettext_lazy as _
from pinax.apps.profiles.models import Profile
from profiles.models import MemberProfile
from siteutils.countries import CountryField, COUNTRY_MAP
from siteutils.models import ServiceProvider
from mailer import send_mail
from datetime import datetime

### APPLICATION SESSIONS
class Session(models.Model):
  name = models.CharField(max_length=200)
  active = models.BooleanField(default=False, editable=False)
  open_date = models.DateField(null=True)
  due_date = models.DateField(null=True)
  close_date = models.DateField(null=True)
  en_instructions = models.TextField("English instructions",
                                     null=True)
  fr_instructions = models.TextField("French instructions",
                                     null=True)
  #completed_application = models.TextField("Thank you message",
  #                                         null=True)
  close_email_subject = models.CharField("Session closing email subject",
                                 null=True, max_length=255)
  close_email_from = models.CharField("Session closing email from", max_length=255,
                                 default="Engineers Without Borders Canada <info@ewb.ca>")
  close_email = models.TextField("Session closing email",
                                 null=True)
  rejection_email_subject = models.CharField("Rejected application email subject",
                                 null=True, max_length=255)
  rejection_email_from = models.CharField("Rejected application email from", max_length=255,
                                 default="Engineers Without Borders Canada <info@ewb.ca>")
  rejection_email = models.TextField("Rejected application email",
                                     null=True)
  
  def application_questions(self):
      return ApplicationQuestion.objects.filter(session=self)
  def interview_questions(self):
      return InterviewQuestion.objects.filter(session=self)
  
  def __unicode__(self):
    return self.name
    
  def complete_applications(self):
    return self.application_set.filter(complete=True)
    
  def draft_applications(self):
    return self.application_set.filter(complete=False)

  def open(self):
    self.active = True
    self.save()
    
  def close(self):
    self.active = False
    self.save()
    
    sender = self.close_email_from
    emails = []
    for app in self.complete_applications():
        emails.append(app.profile.user2.email)
        eval, created = Evaluation.objects.get_or_create(application=app)
        #eval = app.evaluation
        eval.last_email = datetime.now()
        eval.save()
    
    send_mail(subject=self.close_email_subject,
              txtMessage=None,
              htmlMessage=self.close_email,
              fromemail=sender,
              recipients=emails,
              use_template=False)
    
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

class ApplicationQuestion(Question):
  def clone(self):  
      return ApplicationQuestion(question=self.question,
                                 question_order=self.question_order,
                                 session=self.session)
    
  class Meta:
    ordering = ('question_order', 'session')

class InterviewQuestion(Question):
  def clone(self):  
      return InterviewQuestion(question=self.question,
                               question_order=self.question_order,
                               session=self.session)
    
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
  gpa = models.FloatField(null=True, blank=True)
  
  profile = models.ForeignKey(MemberProfile)
  session = models.ForeignKey(Session)
  complete = models.BooleanField(default=False)

  APPLICATION_STATUS = (
      ('d', _('Draft')),
      ('s', _('Submitted')),
      ('r', _('Reviewed')),
      ('i', _('Selected for first interview')),
      ('n', _('Selected for second interview')),
      ('p', _('Decision pending')),
      ('a', _('Accepted - hired')),
      ('u', _('Unsuccessful')),
  )
  status = models.CharField(max_length=1, choices=APPLICATION_STATUS, default='d')
  
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
    
  def completion(self):
    if self.complete:
      return 100
    
    questions = 10      # language, resume, etc
    questions = questions + self.session.application_questions().count()
    
    completed = self.answer_set.count()
    if self.en_writing:
      completed = completed + 1;
    if self.en_reading:
      completed = completed + 1;
    if self.en_speaking:
      completed = completed + 1;
    if self.fr_writing:
      completed = completed + 1;
    if self.fr_reading:
      completed = completed + 1;
    if self.fr_speaking:
      completed = completed + 1;
    if self.schooling:
      completed = completed + 1;
    if self.resume_text:
      completed = completed + 1;
    if self.references:
      completed = completed + 1;
    if self.gpa:
      completed = completed + 1;

    return float(completed) / float(questions) * 100    
    
    
class Answer(models.Model):
  answer = models.TextField()
  application = models.ForeignKey("Application")
  question = models.ForeignKey("Question")


### EVALUATIONS
class EvaluationResponse(models.Model):
  #response = models.PositiveIntegerField(null=True)
  response = models.CharField(max_length=255, null=True)
  evaluation = models.ForeignKey("Evaluation")
  evaluation_criterion = models.ForeignKey("EvaluationCriterion")

class Evaluation(models.Model):
  INTERVIEW_CHOICES = (
      ('Y', _('Yes')),
      ('N', _('No')),
      ('N/A', _('Not needed (hire)')),
  )

  application = models.OneToOneField("Application")
  last_email = models.DateTimeField(blank=True, null=True)
  
  def total_score(self):
    score = 0
    for e in self.evaluationresponse_set.all():
        try:
            if int(e.response):
                score = score + int(e.response)
        except:
            pass

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

  def criteria(self):
    criteria = {}
    for c in self.evaluationresponse_set.all():
        if c.response:
            criteria[c.evaluation_criterion.id] = c.response
    return criteria
    
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
  PLACEMENT_TYPES = (('jf', "Junior Fellow"),
                     ('lt', "Long-term"))
  
  description = models.TextField()
  profile = models.ForeignKey(MemberProfile, related_name='placement')
  type = models.CharField(max_length=2, choices=PLACEMENT_TYPES, default='lt')
  sector = models.ForeignKey(Sector, null=True)
  
  start_date = models.DateField(null=True)
  end_date = models.DateField(null=True)
  town = models.CharField(max_length=100)
  country = CountryField(ewb='placements')

  coach = models.ForeignKey(MemberProfile, related_name='placement_coach', blank=True, null=True)

  flight_request_made = models.BooleanField(default=True)
  deleted = models.BooleanField(default=False)
  
  def country_name(self):
    if self.country and COUNTRY_MAP.has_key(self.country):
      return COUNTRY_MAP[self.country]
    return None

  def type_name(self):
    if self.type:
        for x,y in self.PLACEMENT_TYPES:
            if self.type == x:
                return y
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
  placement = models.ForeignKey(Placement, related_name="insurance")

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
  placement = models.ForeignKey(Placement, related_name='travel')

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

