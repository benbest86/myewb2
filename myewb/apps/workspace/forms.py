"""myEWB workspaces form declarations

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

Last modified on 2010-08-20
@author Francis Kung
"""
from django import forms
from django.forms.fields import email_re

class WorkspaceMoveForm(forms.Form):
    folder = forms.CharField(label="Location",
                             widget=forms.Select)
    
    def __init__(self, *args, **kwargs):
        folders = kwargs.pop('folders', None)
        choices = []
        for folder in folders:
            if folder == '':
                folder = '/'
            choices.append((folder, folder))

        self.base_fields['folder'].choices = choices
        self.base_fields['folder'].widget.choices = choices
            
        super(WorkspaceMoveForm, self).__init__(*args, **kwargs)
    
    def clean_folder(self):
        folder = self.cleaned_data['folder']
        
        # periods can be used to go up in the directory tree...
        if folder.find('.') > -1:
            return ValidationError("Invalid folder (nice hacking attempt)")
        
        return folder
    
class WorkspaceUploadForm(WorkspaceMoveForm):
    file = forms.FileField()

class WorkspaceNewFolderForm(WorkspaceMoveForm):
    name = forms.SlugField()
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if name.find('.') > -1:
            return ValidationError("Folder names cannot contain periods")
        return name
        
class WorkspaceRenameForm(forms.Form):
    newname = forms.SlugField()
    
    def clean_newname(self):
        newname = self.cleaned_data['newname']
        if newname.find('.') > -1:
            return ValidationError("Folder names cannot contain periods")
        return newname
    
class WorkspaceReplaceForm(forms.Form):
    file = forms.FileField()
