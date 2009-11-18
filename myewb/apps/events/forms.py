from django import forms
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
    
    def clean(self):
        if self.cleaned_data['end'] < self.cleaned_data['start']:
            raise forms.ValidationError("End time must be after the start time.")
        
        return self.cleaned_data

    class Meta:
        model = Event
        exclude = ('object_id', 'content_type', 'owner', 'whiteboard')

'''
class EventAddForm(EventForm):
    class Meta(EventForm.Meta):
        exclude = ('object_id', 'content_type', 'owner')

class EventFormWithMedia(EventForm):

    class Media:
        css = {'all':('events_form.css',), }
        js = ('events_form.js',)

'''
