from django import forms

from confcomm.models import ConferenceProfile

# place form definition here

class ConferenceProfileForm(forms.ModelForm):
    class Meta:
        model = ConferenceProfile
