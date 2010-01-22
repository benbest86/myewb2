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
from profiles.forms import UserField, UserSelectionInput
from messages.forms import ComposeForm as OriginalComposeForm
from lxml.html.clean import clean_html, autolink_html

class ComposeForm(OriginalComposeForm):
    """
    A simple default form for private messages.
    """

    recipient = UserField(label=_(u"Recipient"))
    body = forms.CharField(label=_(u"Body"),
        widget=forms.Textarea(attrs={'rows': '12', 'cols':'55', 'class':'tinymce '}))
    
    def clean_body(self):
        body = self.cleaned_data.get('body', '')

        # validate HTML content
        # Additional options at http://codespeak.net/lxml/lxmlhtml.html#cleaning-up-html
        body = clean_html(body)
        body = autolink_html(body)
    
        self.cleaned_data['body'] = body
        return self.cleaned_data['body']
    
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
