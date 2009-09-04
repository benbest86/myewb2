from threadedcomments.forms import ThreadedCommentForm
from threadedcomments.models import ThreadedComment
from mythreadedcomments.models import MyThreadedComment
from lxml.html.clean import clean_html, autolink_html

class MyThreadedCommentForm(ThreadedCommentForm):
    
    def clean_comment(self):
        self.cleaned_data['comment'] = clean_html(self.cleaned_data['comment'])
        self.cleaned_data['comment'] = autolink_html(self.cleaned_data['comment'])
        return self.cleaned_data['comment']
    
    class Meta:
        model = ThreadedComment
        fields = ('comment', 'markup')