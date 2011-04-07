from django import forms
from django.utils.translation import ugettext_lazy as _
from lxml.html.clean import clean_html, autolink_html

from jobboard.models import JobPosting, Skill, Location
from user_search.forms import AutocompleteField

class JobPostingForm(forms.ModelForm):
    skills = AutocompleteField(model=Skill,
                               create=True,
                               chars=1,
                               multi=True,
                               required=False)

    location = AutocompleteField(model=Location,
                                 create=True,
                                 chars=1,
                                 multi=False,
                                 required=False,
                                 help_text='If this posting is location-specific, enter it here. Leave blank if this can be done from any location.')

    class Meta:
        model = JobPosting
        fields = ('name', 'description', 'deadline', 'urgency', 'time_required', 'location', 'skills')

    def clean_skills(self):
        return self.cleaned_data['skills']