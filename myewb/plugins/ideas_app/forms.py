from django import forms
from ideas_app.models import Idea

class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
