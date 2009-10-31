from django import forms
from django.contrib.admin import widgets
from volunteering.models import *

class PlacementForm(forms.ModelForm):
  start_date = forms.DateField(widget=widgets.AdminDateWidget)
  end_date = forms.DateField(widget=widgets.AdminDateWidget)
  class Meta:
    model = Placement

class ApplicationForm(forms.ModelForm):
  class Meta:
    model = Application

class SessionForm(forms.ModelForm):
  class Meta:
    model = Session

class QuestionForm(forms.ModelForm):
  class Meta:
    model = Question

class AnswerForm(forms.ModelForm):
  class Meta:
    model = Answer

class EvaluationCriterionForm(forms.ModelForm):
  class Meta:
    model = EvaluationCriterion

class EvaluationResponseForm(forms.ModelForm):
  class Meta:
    model = EvaluationResponse

class EvaluationForm(forms.ModelForm):
  class Meta:
    model = Evaluation

