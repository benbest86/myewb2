from django import forms

from cgi import escape

from confcomm.models import ConferenceProfile
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

# place form definition here

class ConferenceProfileForm(forms.ModelForm):
    class Meta:
        model = ConferenceProfile
        exclude = ('member_profile', 'updated',)

    def clean(self):
        data = self.cleaned_data
        for f in ['what_now', 'text_interests', 'conference_goals', 'conference_question',]:
            data[f] = escape(data[f])
        return data

class InvitationForm(forms.Form):
    recipient = forms.CharField()
    sender = forms.CharField()
    subject = forms.CharField(max_length=255)
    body = forms.CharField()

    def clean_recipient(self):
        data = self.cleaned_data['recipient']
        try:
            r = User.objects.get(username=data)
            if not r.email:
                raise forms.ValidationError(_('No email found for recipient with username %s.' % data))
            self.recipient_email = r.email
            self.recipient = r
        except forms.ValidationError, e:
            raise e
        except Exception, e:
            raise forms.ValidationError(_('Could not find recipient with username %s.' % data))
        return data

    def clean_sender(self):
        data = self.cleaned_data['sender']
        try:
            s = User.objects.get(username=data)
            if not s.email:
                raise forms.ValidationError(_('No email found for sender with username %s.' % data))
            self.sender_email = s.email
            self.sender = s
        except forms.ValidationError, e:
            raise e
        except Exception, e:
            raise forms.ValidationError(_('Could not find sender with username %s.' % data))
        return data

    def clean(self):
        data = self.cleaned_data
        for f in ['body', 'subject']:
            data[f] = escape(data[f])
        return data
