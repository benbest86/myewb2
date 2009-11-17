from django import forms
from django.contrib.admin import widgets
from volunteering.models import *

class SessionForm(forms.ModelForm):
  open_date = forms.DateField(widget=widgets.AdminDateWidget)
  close_date = forms.DateField(widget=widgets.AdminDateWidget)
  due_date = forms.DateField(widget=widgets.AdminDateWidget)
  email_sent = forms.BooleanField()
  class Meta:
    model = Session

class ApplicationForm(forms.ModelForm):
  class Meta:
    model = Application

class QuestionForm(forms.ModelForm):
  class Meta:
    model = Question

class AnswerForm(forms.ModelForm):
  class Meta:
    model = Answer

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

class EvaluationCriterionForm(forms.ModelForm):
  class Meta:
    model = EvaluationCriterion

class EvaluationResponseForm(forms.ModelForm):
  class Meta:
    model = EvaluationResponse

class EvaluationForm(forms.ModelForm):
  class Meta:
    model = Evaluation

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

class CaseStudyForm(forms.ModelForm):
  class Meta:
    model = CaseStudy

class SendingGroupForm(forms.ModelForm):
  class Meta:
    model = SendingGroup


