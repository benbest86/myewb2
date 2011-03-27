from django import forms
from django.utils.translation import ugettext_lazy as _
from lxml.html.clean import clean_html, autolink_html

from jobboard.models import JobPosting

class JobPostingForm(forms.ModelForm):

    class Meta:
        model = JobPosting
        fields = ('name', 'description', 'deadline', 'urgency', 'time_required', 'skills')
