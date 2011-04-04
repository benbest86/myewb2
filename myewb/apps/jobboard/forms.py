from django import forms
from django.utils.translation import ugettext_lazy as _
from lxml.html.clean import clean_html, autolink_html

from jobboard.models import JobPosting, Skill
from user_search.forms import AutocompleteField

class JobPostingForm(forms.ModelForm):
    skills = AutocompleteField(model=Skill,
                               create=True,
                               chars=1,
                               multi=True)

    class Meta:
        model = JobPosting
        fields = ('name', 'description', 'deadline', 'urgency', 'time_required', 'skills')
