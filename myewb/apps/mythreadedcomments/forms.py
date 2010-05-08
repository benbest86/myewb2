from django import forms
from django.core.exceptions import ObjectDoesNotExist
from threadedcomments.forms import ThreadedCommentForm, FreeThreadedCommentForm
from threadedcomments.models import ThreadedComment, FreeThreadedComment
from tag_app.models import TagAlias
from lxml.html.clean import clean_html, autolink_html

class MyThreadedCommentForm(ThreadedCommentForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))
    tags = forms.CharField()
    
    def clean_comment(self):
        self.cleaned_data['comment'] = clean_html(self.cleaned_data['comment'])
        self.cleaned_data['comment'] = autolink_html(self.cleaned_data['comment'])
        return self.cleaned_data['comment']
    
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
                tags += alias.tag.name + ","
                # should the alias just store the tag's text, instead of a 
                # reference to the object, for db efficiency?
                
            # otherwise, leave it as is...
            except ObjectDoesNotExist:
                tags += tag + ","
        
        return tags

    class Meta:
        model = ThreadedComment
        fields = ('comment', 'markup')
        
class MyFreeThreadedCommentForm(FreeThreadedCommentForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'class':'tinymce '}))
    tags = forms.CharField()

    def clean_comment(self):
        self.cleaned_data['comment'] = clean_html(self.cleaned_data['comment'])
        self.cleaned_data['comment'] = autolink_html(self.cleaned_data['comment'])
        return self.cleaned_data['comment']

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
                tags += alias.tag.name + ","
                # should the alias just store the tag's text, instead of a 
                # reference to the object, for db efficiency?
                
            # otherwise, leave it as is...
            except ObjectDoesNotExist:
                tags += tag + ","
        
        return tags

    class Meta:
        model = FreeThreadedComment
        fields = ('comment', 'markup')