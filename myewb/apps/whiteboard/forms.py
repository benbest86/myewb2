# -*- coding: utf-8 -*-

from django import forms
from django.forms import widgets
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from lxml.html.clean import clean_html, autolink_html

from whiteboard.models import Whiteboard
from wiki.utils import get_ct

# hmm,why can't I extend wiki.forms.ArticleForm ? =(
class WhiteboardForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': '20', 'class':'tinymce '}))

    comment = forms.CharField(required=False, max_length=50)

    user_ip = forms.CharField(widget=forms.HiddenInput)

    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.all(),
        required=False,
        widget=forms.HiddenInput)
    object_id = forms.IntegerField(required=False,
                                   widget=forms.HiddenInput)

    action = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Whiteboard
        exclude = ('creator', 'creator_ip', 'removed',
                   'group', 'created_at', 'last_update',
                   'summary', 'title', 'markup', 'tags', 'parent_group',
                   'converted')

    def clean_content(self):
        """ Do our usual HTML cleanup.
        Do we want to mangle the markup field to always be "html"?
        """
        self.cleaned_data['content'] = clean_html(self.cleaned_data['content'])
        self.cleaned_data['content'] = autolink_html(self.cleaned_data['content'])
        return self.cleaned_data['content']
        
        
    def clean_title(self):
        """ Whiteboard title is always the group slug.
        Really, whiteboards don't need titles, but using the slug enforces
        uniqueness... (can relax this if we do full wikis for groups)
        (actually, is this even called, since "title" is in the exclude list?)
        """
        
        ctype = get_ct(self.cleaned_data['content_type'])
        group = ctype.get_object_for_this_type(pk=self.cleaned_data['object_id'])
        self.cleaned_data['title'] = group.slug

        return self.cleaned_data['title']

    def clean(self):
        super(WhiteboardForm, self).clean()
        kw = {}

        if self.cleaned_data['action'] == 'create':
            try:
                kw['title'] = self.cleaned_data['title']
                kw['content_type'] = self.cleaned_data['content_type']
                kw['object_id'] = self.cleaned_data['object_id']
            except KeyError:
                pass # some error in this fields
            else:
                if Whiteboard.objects.filter(**kw).count():
                    raise forms.ValidationError(
                        _("An article with this title already exists."))

        return self.cleaned_data

    def save(self):
        # 0 - Extra data
        editor_ip = self.cleaned_data['user_ip']
        comment = self.cleaned_data['comment']

        # 1 - Get the old stuff before saving
        if self.instance.id is None:
            old_title = old_content = old_markup = ''
            new = True
        else:
            old_title = self.instance.title
            old_content = self.instance.content
            old_markup = self.instance.markup
            new = False

        # 2 - Save the Article
        article = super(WhiteboardForm, self).save()

        # 3 - Set creator and group
        editor = getattr(self, 'editor', None)
        group = getattr(self, 'group', None)
        if new:
            article.creator_ip = editor_ip
            if editor is not None:
                article.creator = editor
                article.group = group
            article.save()

        # 4 - Create new revision
        changeset = article.new_revision(
            old_content, old_title, old_markup,
            comment, editor_ip, editor)

        return article, changeset
