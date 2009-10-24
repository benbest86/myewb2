from django import forms
from threadedcomments.forms import ThreadedCommentForm, FreeThreadedCommentForm
from threadedcomments.models import ThreadedComment, FreeThreadedComment
from lxml.html.clean import clean_html, autolink_html

class MyThreadedCommentForm(ThreadedCommentForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))
    
    def clean_comment(self):
        self.cleaned_data['comment'] = clean_html(self.cleaned_data['comment'])
        self.cleaned_data['comment'] = autolink_html(self.cleaned_data['comment'])
        return self.cleaned_data['comment']
    
    class Meta:
        model = ThreadedComment
        fields = ('comment', 'markup')
        
class MyFreeThreadedCommentForm(FreeThreadedCommentForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))

    def clean_comment(self):
        self.cleaned_data['comment'] = clean_html(self.cleaned_data['comment'])
        self.cleaned_data['comment'] = autolink_html(self.cleaned_data['comment'])
        return self.cleaned_data['comment']

    class Meta:
        model = FreeThreadedComment
        fields = ('comment', 'markup')