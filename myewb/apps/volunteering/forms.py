from django import forms
from django.contrib.admin import widgets

from lxml.html.clean import clean_html, autolink_html, Cleaner
from siteutils.helpers import autolink_email

from volunteering.models import *

# do HTML validation and auto-linking
def html_clean(body):
  # validate HTML content
  # Additional options at http://codespeak.net/lxml/lxmlhtml.html#cleaning-up-html
  body = clean_html(body)
  body = autolink_html(body)
    
  # emails too
  body = autolink_email(body)
    
  return body

### APPLICATION SESSIONS
class SessionForm(forms.ModelForm):
  open_date = forms.DateField(widget=widgets.AdminDateWidget)
  close_date = forms.DateField(widget=widgets.AdminDateWidget)
  due_date = forms.DateField(widget=widgets.AdminDateWidget)
  email_sent = forms.BooleanField(required=False)

  en_instructions = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))
  fr_instructions = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))
  completed_application = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))
  close_email = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))
  rejection_email = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))
  
  class Meta:
    model = Session
    
  def clean_en_instructions(self):
      return html_clean(self.cleaned_data.get('en_instructions', ''))
  
  def clean_fr_instructions(self):
      return html_clean(self.cleaned_data.get('fr_instructions', ''))
  
  def clean_completed_applications(self):
      return html_clean(self.cleaned_data.get('completed_applications', ''))
  
  def clean_close_email(self):
      return html_clean(self.cleaned_data.get('close_email', ''))
  
  def clean_rejection_email(self):
      return html_clean(self.cleaned_data.get('rejection_email', ''))

class QuestionForm(forms.ModelForm):
  class Meta:
    model = Question
    fields = ('question')
    
class EvaluationCriterionForm(forms.ModelForm):
  class Meta:
    model = EvaluationCriterion
    fields = ('criteria', 'column_header')

class CaseStudyForm(forms.ModelForm):
  class Meta:
    model = CaseStudy


### APPLICATIONS
class ApplicationForm(forms.ModelForm):
  class Meta:
    model = Application

class AnswerForm(forms.ModelForm):
  class Meta:
    model = Answer


### EVALUATION
class EvaluationResponseForm(forms.ModelForm):
  class Meta:
    model = EvaluationResponse

class EvaluationForm(forms.ModelForm):
  class Meta:
    model = Evaluation


### PLACEMENT TRACKING
class SectorForm(forms.ModelForm):
  class Meta:
    model = Sector

class PlacementForm(forms.ModelForm):
  start_date = forms.DateField(widget=widgets.AdminDateWidget)
  end_date = forms.DateField(widget=widgets.AdminDateWidget)
  class Meta:
    model = Placement

class StipendForm(forms.ModelForm):
  class Meta:
    model = Stipend

class InsuranceInstanceForm(forms.ModelForm):
  start_date = forms.DateField(widget=widgets.AdminDateWidget)
  end_date = forms.DateField(widget=widgets.AdminDateWidget)
  insurance_company = forms.ModelChoiceField(queryset=ServiceProvider.objects.filter(type="insurance"))
  price = forms.DecimalField(max_digits=10, decimal_places=2)
  class Meta:
    model = InsuranceInstance

class TravelSegmentForm(forms.ModelForm):
  start_date_time = forms.DateTimeField(widget=widgets.AdminSplitDateTime)
  end_date_time = forms.DateTimeField(widget=widgets.AdminSplitDateTime)
  class Meta:
    model = TravelSegment

class SendingGroupForm(forms.ModelForm):
  class Meta:
    model = SendingGroup

