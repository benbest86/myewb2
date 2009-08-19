"""myEWB GroupTopic forms

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Created on: 2009-08-13
@author: Joshua Gorner
"""

from django import forms

from group_topics.models import GroupTopic

class GroupTopicForm(forms.ModelForm):
    
    body = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))

    class Meta:
        model = GroupTopic
        fields = ('title', 'body', 'tags', 'send_as_email')