"""myEWB CHAMP form declarations

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""
from django import forms
from django.utils.translation import ugettext_lazy as _

from champ.models import *

class ChampForm(forms.ModelForm):
    name = forms.CharField(required=True)
    date = forms.DateField(required=True)
    
    numVolunteers = forms.CharField(label=_('# of Volunteers'),
                                    help_text=_("how many individuals were involved in planning and running the activity? (This can be filled in later, but the activity cannot be confirmed until it's filled in.)"),
                                    required=False)
    prepHours = forms.CharField(label=_("Person-hours of planning/preparation"),
                                help_text=_("how many person-hours went into planning/preparing for the activity? (This can be filled in later, but the activity cannot be confirmed until it's filled in.)"),
                                required=False)
    execHours = forms.CharField(label=_("Person-hours of execution"),
                                help_text=_("how many person-hours went into running the activity? (This can be filled in later, but the activity cannot be confirmed until it's filled in.)"),
                                required=False)

    class Meta:
        model = Activity
        fields = ('name', 'date', 'numVolunteers', 'prepHours', 'execHours')
    
class MemberLearningForm(forms.ModelForm):
    class Meta:
        model = MemberLearningMetrics
        
class SchoolOutreachForm(forms.ModelForm):
    class Meta:
        model = SchoolOutreachMetrics
        
class FunctioningForm(forms.ModelForm):
    class Meta:
        model = FunctioningMetrics
        
class PublicEngagementForm(forms.ModelForm):
    class Meta:
        model = PublicEngagementMetrics
        
class PublicAdvocacyForm(forms.ModelForm):
    class Meta:
        model = PublicAdvocacyMetrics
        
class PublicationForm(forms.ModelForm):
    class Meta:
        model = PublicationMetrics
        
class FundraisingForm(forms.ModelForm):
    class Meta:
        model = FundraisingMetrics
        
class WorkplaceOutreachForm(forms.ModelForm):
    class Meta:
        model = WorkplaceOutreachMetrics
        
class CurriculumEnhancementForm(forms.ModelForm):
    class Meta:
        model = CurriculumEnhancementMetrics
        
METRICFORMS = {'ml': MemberLearningForm,
               'so': SchoolOutreachForm,
               'func': FunctioningForm,
               'pe': PublicEngagementForm,
               'pa': PublicAdvocacyForm,
               'pub': PublicationForm,
               'fund': FundraisingForm,
               'wo': WorkplaceOutreachForm,
               'ce': CurriculumEnhancementForm}

