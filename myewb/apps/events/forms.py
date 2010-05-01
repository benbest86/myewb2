from django import forms

from base_groups.models import BaseGroup
from communities.models import Community
from networks.models import Network
from events.models import Event

class EventForm(forms.ModelForm):

    start = forms.DateTimeField(('%m/%d/%Y %H:%M',),
           widget=forms.SplitDateTimeWidget
            #widget=forms.SplitDateTimeWidget(
                #date_format='%m/%d/%Y',
                #time_format='%H:%M',
            #)
    )

    end = forms.DateTimeField(('%m/%d/%Y %H:%M',),
           widget=forms.SplitDateTimeWidget
           )
    
    postal_code = forms.CharField(required=False,
                                  help_text='This will not be publicly visible, but will eventually be used to determine events near a user')
    
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))


    def clean(self):
        if self.cleaned_data['end'] < self.cleaned_data['start']:
            raise forms.ValidationError("End time must be after the start time.")
        
        return self.cleaned_data

    class Meta:
        model = Event
        exclude = ('object_id', 'content_type', 'owner', 'whiteboard', 'parent_group')

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

'''
class EventAddForm(EventForm):
    class Meta(EventForm.Meta):
        exclude = ('object_id', 'content_type', 'owner')

class EventFormWithMedia(EventForm):

    class Media:
        css = {'all':('events_form.css',), }
        js = ('events_form.js',)

'''
