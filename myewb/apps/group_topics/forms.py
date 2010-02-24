"""myEWB GroupTopic forms

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
Some code derived from Pinax, copyright 2008-2009 James Tauber and Pinax Team, licensed under the MIT License

Created on: 2009-08-13
@author: Joshua Gorner
"""

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from group_topics.models import GroupTopic
from tag_app.models import TagAlias

class GroupTopicForm(forms.ModelForm):
    
    body = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))
    sender = forms.ChoiceField(label=_('Sender'),
                               choices=(),
                               required=False)

    class Meta:
        model = GroupTopic
        fields = ('title', 'body', 'tags', 'send_as_email')
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        group = kwargs.pop('group', None)
        super(GroupTopicForm, self).__init__(*args, **kwargs)

        # build list of potential "from" addresses
        if user and group and group.user_is_admin(user):
            emaillist = user.get_profile().email_addresses()
            emails = []
            for email in emaillist:
                emails.append((email.email, "%s %s <%s>" % (user.get_profile().first_name,
                                                            user.get_profile().last_name, 
                                                            email.email)))
                
            if group.user_is_admin(user):
                emails.append((group.from_email,
                               "%s <%s>" % (group.from_name, group.from_email)))
            
            if user.is_staff:
                emails.append(("info@ewb.ca",
                               "EWB-ISF Canada <info@ewb.ca>"))
            
            self.fields['sender'].choices = emails
            
        # these people don't have permission to send email...
        else:
            del self.fields['send_as_email']
            del self.fields['sender']

        #self.fields['parent_group'].initial = group
        
    # Check tag aliases: see tag_app.TagAlias
    # (should we delegate this to tag_app? seems to fit better there...)
    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')

        # the jquery autocomplete enforces the commas, but django's tagging
        # is actually much more flexible (supports quotes, etc).  If we take 
        # advantage of that, we'll need to update our multiple tag recognition
        # as well
        taglist = tags.split(',')
        tags = ""
        for tag in taglist:
            tag = tag.strip()
            
            # look up alias - if one exists, use the real tag
            try:
                alias = TagAlias.objects.get(alias=tag)
                tags += alias.tag.name
                # should the alias just store the tag's text, instead of a 
                # reference to the object, for db efficiency?
                
            # otherwise, leave it as is...
            except ObjectDoesNotExist:
                tags += tag + ","
        
        return tags
        
