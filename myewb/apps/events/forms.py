from django import forms
from django.utils.translation import ugettext_lazy as _
from lxml.html.clean import clean_html, autolink_html

from base_groups.models import BaseGroup
from communities.models import Community
from networks.models import Network
from events.models import Event

class EventForm(forms.ModelForm):

    start = forms.DateTimeField(widget=forms.SplitDateTimeWidget)
    end = forms.DateTimeField(widget=forms.SplitDateTimeWidget)
    
    postal_code = forms.CharField(required=False,
                                  help_text='This will not be publicly visible, but will eventually be used to determine events near a user')
    
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))

    def clean(self):
        # why does this get called before field validation that ensures they are filled in???
        if self.cleaned_data.get('end', None) and self.cleaned_data.get('start', None):
            if self.cleaned_data['end'] < self.cleaned_data['start']:
                raise forms.ValidationError("End time must be after the start time.")
        
        return self.cleaned_data

    class Meta:
        model = Event
        exclude = ('object_id', 'content_type', 'owner', 'whiteboard',
                   'parent_group', 'converted')

class GroupEventForm(EventForm):
    group = forms.ChoiceField(choices=[(0,'None (my personal calendar)')])
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super(GroupEventForm, self).__init__(*args, **kwargs)

        if user:
            if user.has_module_perms("basegroups"):
                networks = Network.objects.all()
                communities = Community.objects.all()
            else:
                networks = Network.objects.filter(members__user=user,
                                                  members__is_admin=True)
                communities = Community.objects.filter(members__user=user,
                                                       members__is_admin=True)
            groups = []
            for n in networks:
                groups.append(("n%d" % n.pk, n.name))
            for c in communities:
                groups.append(("c%d" % c.pk, c.name))
            self.fields['group'].choices.extend(groups)
            
class EventEmailForm(forms.Form):
    subject = forms.CharField(max_length=250)
    body = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))
    sender = forms.ChoiceField(label=_('Sender'),
                               choices=(),
                               required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        group = kwargs.pop('group', None)
        super(EventEmailForm, self).__init__(*args, **kwargs)

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
            del self.fields['sender']
        
    def clean_body(self):
        body = self.cleaned_data.get('body', '')

        # validate HTML content
        # Additional options at http://codespeak.net/lxml/lxmlhtml.html#cleaning-up-html
        body = clean_html(body)
        #body = autolink_html(body)
    
        self.cleaned_data['body'] = body
        return self.cleaned_data['body']

'''
class EventAddForm(EventForm):
    class Meta(EventForm.Meta):
        exclude = ('object_id', 'content_type', 'owner')

class EventFormWithMedia(EventForm):

    class Media:
        css = {'all':('events_form.css',), }
        js = ('events_form.js',)

'''
