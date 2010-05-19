"""
import datetime
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_noop
from django.contrib.auth.models import User

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from messages.models import Message
from messages.fields import CommaSeparatedUserField
"""
from django import forms
from django.utils.translation import ugettext_lazy as _
from user_search.forms import MultipleUserField
from messages.forms import ComposeForm as OriginalComposeForm
from lxml.html.clean import clean_html, autolink_html

from friends.models import Friendship
from base_groups.models import BaseGroup, GroupMember

class ComposeForm(OriginalComposeForm):
    """
    A simple default form for private messages.
    """

    recipient = MultipleUserField(label=_(u"Recipient"))
    body = forms.CharField(label=_(u"Body"),
        widget=forms.Textarea(attrs={'rows': '12', 'cols':'55', 'class':'tinymce '}))

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        return super(ComposeForm, self).__init__(*args, **kwargs)
    
    def clean_body(self):
        body = self.cleaned_data.get('body', '')

        # validate HTML content
        # Additional options at http://codespeak.net/lxml/lxmlhtml.html#cleaning-up-html
        body = clean_html(body)
        body = autolink_html(body)
    
        self.cleaned_data['body'] = body
        return self.cleaned_data['body']

    def clean(self):
        if not self.sender:
            raise forms.ValidationError('Internal error.')
        
        super(ComposeForm, self).clean()
        
        if not self.sender.has_module_perms("profiles"):
            recipients = self.cleaned_data['recipient']
            for r in recipients:
                if not Friendship.objects.are_friends(self.sender, r):
                    # should be in BaseGroup manager, not here and also account_extra.models (ie, User.get_groups())
                    grps = BaseGroup.objects.filter(member_users=self.sender).exclude(model="LogisticalGroup")
                    
                    # should probably also be in a BaseGroup manager somewhere...!
                    gm = GroupMember.objects.filter(user=r, group__in=grps).count()
                    if gm == 0:
                        raise forms.ValidationError('You can only send messages to friends or people in the same chapter')
            
        return self.cleaned_data
    
    """
    #recipient = CommaSeparatedUserField(label=_(u"Recipient"))
    subject = forms.CharField(label=_(u"Subject123"))
    body = forms.CharField(label=_(u"Body"),
        widget=forms.Textarea(attrs={'rows': '12', 'cols':'55'}))
    
        
    def __init__(self, *args, **kwargs):
        recipient_filter = kwargs.pop('recipient_filter', None)
        super(ComposeForm, self).__init__(*args, **kwargs)
        if recipient_filter is not None:
            self.fields['recipient']._recipient_filter = recipient_filter
    
                
    def save(self, sender, parent_msg=None):
        recipients = self.cleaned_data['recipient']
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        message_list = []
        for r in recipients:
            msg = Message(
                sender = sender,
                recipient = r,
                subject = subject,
                body = body,
            )
            if parent_msg is not None:
                msg.parent_msg = parent_msg
                parent_msg.replied_at = datetime.datetime.now()
                parent_msg.save()
            msg.save()
            message_list.append(msg)
            if notification:
                if parent_msg is not None:
                    notification.send([sender], "messages_replied", {'message': msg,})
                    notification.send(recipients, "messages_reply_received", {'message': msg,})
                else:
                    notification.send([sender], "messages_sent", {'message': msg,})
                    notification.send(recipients, "messages_received", {'message': msg,})
        return message_list
    """
