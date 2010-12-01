"""myEWB CHAMP form declarations

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""
from django import forms
from django.utils.translation import ugettext_lazy as _
from haystack.forms import SearchForm

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
    
    def ensure_int(self, field):
        data = self.cleaned_data[field]
        if data == '':
            return None
        else:
            try:
                return int(data)
            except ValueError:
                raise forms.ValidationError("Please enter a number")
            
    # why doesn't django's auto-clean work???
    def clean_numVolunteers(self):
        return self.ensure_int('numVolunteers')
    
    def clean_prepHours(self):
        return self.ensure_int('prepHours')
    
    def clean_execHours(self):
        return self.ensure_int('execHours')
    
    class Meta:
        model = Activity
        fields = ('name', 'date', 'rating', 'numVolunteers', 'prepHours', 'execHours')
        
class ImpactForm(forms.ModelForm):
    class Meta:
        model = ImpactMetrics
    
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
        
class AdvocacyLettersForm(forms.ModelForm):
    class Meta:
        model = AdvocacyLettersMetrics
        
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
        
METRICFORMS = {'all': ImpactForm,
               'ml': MemberLearningForm,
               'so': SchoolOutreachForm,
               'func': FunctioningForm,
               'pe': PublicEngagementForm,
               'pa': PublicAdvocacyForm,
               'pub': PublicationForm,
               'fund': FundraisingForm,
               'wo': WorkplaceOutreachForm,
               'ce': CurriculumEnhancementForm}

class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = ('snapshot', 'highlight', 'challenge', 'leadership', 'learning', 'innovation', 'yearplan', 'office', 'private')
        
class YearPlanForm(forms.ModelForm):
    class Meta:
        model = YearPlan
        exclude = ('year', 'group', 'last_modified', 'last_editor')
        
class CHAMPSearchForm(SearchForm):
    q = forms.CharField(required=False, label=_('Keyword'))
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)
    
    rating = forms.ChoiceField(required=False,
                               choices=(('1', 'Any'),
                                        ('2', 'At least 2 stars'),
                                        ('3', 'At least 3 stars'),
                                        ('4', 'At least 4 stars'),
                                        ('5', '5 stars - only the best!')))
    metrics = forms.MultipleChoiceField(required=False,
                                        label='Event types',
                                        choices=ALLMETRICS,
                                        widget=forms.CheckboxSelectMultiple)

    def search(self):
        self.clean()
        if not self.cleaned_data.get('q', None):
            return None
        
        # First, store the SearchQuerySet received from other processing.
        sqs = super(CHAMPSearchForm, self).search()

        # Check to see if a start_date was chosen.
        if self.cleaned_data['start_date']:
            sqs = sqs.filter(pub_date__gte=self.cleaned_data['start_date'])

        # Check to see if an end_date was chosen.
        if self.cleaned_data['end_date']:
            sqs = sqs.filter(pub_date__lte=self.cleaned_data['end_date'])

        if self.cleaned_data['rating']:
            try:
                rating = int(self.cleaned_data['rating'])
                sqs = sqs.filter(rating__gte=rating)
            except:
                pass
            
        if self.cleaned_data['metrics']:
            for m in self.cleaned_data['metrics']:
                sqs = sqs.filter(metrics=m)
        
        return sqs
    