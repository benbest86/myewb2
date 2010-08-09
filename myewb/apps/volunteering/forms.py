from django import forms
from django.contrib.admin import widgets
from django.contrib.auth.models import User

from lxml.html.clean import clean_html, autolink_html, Cleaner

from profiles.models import MemberProfile
from user_search.forms import UserField, AutocompleteField
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

  en_instructions = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))
  fr_instructions = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))
  #completed_application = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))
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

class ApplicationQuestionForm(forms.ModelForm):
  class Meta:
    model = ApplicationQuestion
    fields = ('question')
    
class InterviewQuestionForm(forms.ModelForm):
  class Meta:
    model = InterviewQuestion
    fields = ('question')
    
class EvaluationCriterionForm(forms.ModelForm):
  class Meta:
    model = EvaluationCriterion
    fields = ('criteria', 'column_header')

class CaseStudyForm(forms.ModelForm):
  class Meta:
    model = CaseStudy


### APPLICATIONS
onetofive = ((0,''), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5))
class ApplicationForm(forms.ModelForm):
    en_writing = forms.CharField(widget=forms.Select(choices=onetofive), required=False)
    en_reading = forms.CharField(widget=forms.Select(choices=onetofive), required=False)
    en_speaking = forms.CharField(widget=forms.Select(choices=onetofive), required=False)
    fr_writing = forms.CharField(widget=forms.Select(choices=onetofive), required=False)
    fr_reading = forms.CharField(widget=forms.Select(choices=onetofive), required=False)
    fr_speaking = forms.CharField(widget=forms.Select(choices=onetofive), required=False)

#    schooling = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}),
#                                required=False)
#    resume_text = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}),	
#                                  required=False)
#    references = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}),
#                                 required=False)

    def clean_schooling(self):
        data = self.cleaned_data.get('schooling', '')
        if data:
            return html_clean(data)

    def clean_resume_text(self):
        data = self.cleaned_data.get('resume_text', '')
        if data:
            return html_clean(data)

    def clean_references(self):
        data = self.cleaned_data.get('references', '')
        if data:
            return html_clean(data)

    class Meta:
        model = Application
        fields = ('en_writing', 'en_reading', 'en_speaking',
                  'fr_writing', 'fr_reading', 'fr_speaking',
                  'schooling', 'resume_text', 'references', 'gpa')
    
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
  sector = AutocompleteField(model=Sector, create=True)
  profile = AutocompleteField(label="Name", model=MemberProfile, create=False, chars=3)
  coach = AutocompleteField(model=MemberProfile, create=False, chars=3, required=False)
  
  class Meta:
    model = Placement
    exclude=('deleted', 'flight_request_made')
    
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

class EmailForm(forms.Form):
    subject = forms.CharField(max_length=250)
    body = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))
    sendername = forms.CharField(max_length=75)
    senderemail = forms.EmailField()

    def clean_body(self):
        body = self.cleaned_data.get('body', '')

        # validate HTML content
        # Additional options at http://codespeak.net/lxml/lxmlhtml.html#cleaning-up-html
        body = clean_html(body)
    
        self.cleaned_data['body'] = body
        return self.cleaned_data['body']
