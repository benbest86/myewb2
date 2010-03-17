"""myEWB searching views

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

Created on: 2010-03-17
@author: Francis Kung
"""

from django import forms
from haystack.forms import ModelSearchForm


class DateAuthorSearchForm(ModelSearchForm):
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)
    author = forms.CharField(required=False, max_length=255)

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(DateAuthorSearchForm, self).search()

        # Check to see if a start_date was chosen.
        if self.cleaned_data['start_date']:
            sqs = sqs.filter(pub_date__gte=self.cleaned_data['start_date'])

        # Check to see if an end_date was chosen.
        if self.cleaned_data['end_date']:
            sqs = sqs.filter(pub_date__lte=self.cleaned_data['end_date'])

        # Check to see if an author was chosen.
        if self.cleaned_data['author']:
            sqs = sqs.filter(author=sqs.query.clean(self.cleaned_data['author']))

        return sqs