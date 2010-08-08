"""myEWB profile forms

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on 2009-06-22
Last modified on 2009-12-29
@author Joshua Gorner, Francis Kung, Ben Best
"""
from settings import STATIC_URL
from django import forms
from django.forms.util import flatatt, smart_unicode
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from siteutils.shortcuts import get_object_or_none

class UserSearchForm(forms.Form):
    usi_first_name = forms.CharField(label="First name", required=False)
    usi_last_name = forms.CharField(label="Last name", required=False)
    usi_chapters = [('none', _('Any chapter'))]
    #chapter = forms.ChoiceField(choices=chapters, required=False)
  
    def __init__(self, *args, **kwargs):
        chapterlist = kwargs.pop('chapters', None)
        
        self.base_fields['usi_first_name'].initial = kwargs.pop('first_name', None)
        self.base_fields['usi_last_name'].initial = kwargs.pop('last_name', None)
  
        """
        for chapter in chapterlist:
            try:
                i = self.base_fields['chapter'].choices.index((chapter.slug, chapter.chapter_info.chapter_name))
            except ValueError:
                self.base_fields['chapter'].choices.append((chapter.slug, chapter.chapter_info.chapter_name))
        
        self.base_fields['chapter'].initial = kwargs.pop('chapter', None)
        """

        super(UserSearchForm, self).__init__(*args, **kwargs)
        
class MultipleUserSelectionInput(forms.MultipleHiddenInput):
    """
    Used to select one or more users, which are shown as labels
    corresponding to the users' real names, but stored as hidden
    inputs (usernames) behind the scenes.
    """
    
    is_hidden = False
    
    class Media:
        css = {
            "all": (STATIC_URL + 'css/user_selection.css',)
        }
        js = (STATIC_URL + 'js/user_selection.js',)

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []        
        users = []
        
        for v in value:
        	if isinstance(v, User):
        		users.append(v)
        	else:
        		try:
        			u = User.objects.get(username=v)
        			users.append(u)
        		except User.DoesNotExist:
        			pass
        t = loader.get_template('user_search/user_selection_input.html')
        c = Context({'users': users, 'field_name': name, 'multiuser': True})
        return mark_safe(t.render(c))
        
class MultipleUserField(forms.Field):
 	# most of this is from messages.fields.CommaSeparatedUserField.clean
    widget = MultipleUserSelectionInput

    def __init__(self, *args, **kwargs):
        recipient_filter = kwargs.pop('recipient_filter', None)
        self._recipient_filter = recipient_filter
        super(MultipleUserField, self).__init__(*args, **kwargs)

    def clean(self, value):
    	if not value:
    		if self.required:
    			raise forms.ValidationError(_(u"Please select a recipient"))
    		else:
    			return ''
        
        #if isinstance(value, (list, tuple)):
       # 	return value
        
        try:
        	value.remove('')
        except:
        	pass
        
        names = set(value)
        names_set = set([name.strip() for name in names])
        users = list(User.objects.filter(username__in=names_set))
        unknown_names = names_set ^ set([user.username for user in users])
        
        recipient_filter = self._recipient_filter
        invalid_users = []
        if recipient_filter is not None:
        	for r in users:
        		if recipient_filter(r) is False:
        			users.remove(r)
        			invalid_users.append(r.username)
        			
        if unknown_names or invalid_users:
            raise forms.ValidationError(_(u"The following usernames are incorrect: %(users)s") % {'users': ', '.join(list(unknown_names)+invalid_users)})
        
        return users
        
class UserSelectionInput(forms.HiddenInput):
    """
    Used to select a single user.
    Simplified version of MultipleUserSelectionInput.
    """
    
    is_hidden = False
    
    class Media:
        css = {
            "all": (STATIC_URL + 'css/user_selection.css',)
        }
        js = (STATIC_URL + 'js/user_selection.js',)

    def render(self, name, value, attrs=None, choices=()):
        user = None
        if isinstance(value, User):
            user = value
        else:
            try:
                user = User.objects.get(username=value)
            except User.DoesNotExist:
                pass
        
        if user:
            users = [user]
        else:
            users = None
        
        t = loader.get_template('user_search/user_selection_input.html')
        c = Context({'users': users, 'field_name': name, 'multiuser': False})
        return mark_safe(t.render(c))
        
class UserField(forms.Field):
    widget = UserSelectionInput

    def __init__(self, *args, **kwargs):
        recipient_filter = kwargs.pop('recipient_filter', None)
        self._recipient_filter = recipient_filter
        super(UserField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value:
            if self.required:
                raise forms.ValidationError(_(u"Please select a recipient"))
            else:
                return ''

        user = None
        try:
            user = User.objects.get(username=value)
        except:
            pass
        
        recipient_filter = self._recipient_filter
        if recipient_filter is not None:
            if recipient_filter(user) is False:
                user = None
                    
        if user == None:
            raise forms.ValidationError(_(u"Invalid user"))
            
        return user
        
class SampleUserSearchForm(forms.Form):
    to = UserField(required=False)
    cc = UserField(required=False)
    bcc = UserField(required=False)

class SampleMultiUserSearchForm(forms.Form):
    to = MultipleUserField(required=False)
    cc = MultipleUserField(required=False)
    bcc = MultipleUserField(required=False)

class AutocompleteField(forms.CharField):
    
    def __init__(self, model, create, chars=1, *args, **kwargs):
        self.model = model
        self.create = create
        self.chars = chars
        
        self.widget = AutocompleteWidget(model=model, create=create, chars=chars)    
        super(AutocompleteField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(AutocompleteField, self).clean(value)
        
        obj = get_object_or_none(self.model, name=value)
        if obj:
            return obj
        
        if self.create:
            obj = self.model(name=value)
            obj.save()
            return obj
        else:
            raise forms.ValidationError("Invalid choice")

class AutocompleteWidget(forms.TextInput):
    def __init__(self, model, create, chars, options={}, attrs={}):
        self.model = model
        self.mustmatch = not create
        self.chars = chars
        self.options = options

        self.attrs = {'autocomplete': 'off'}
        self.attrs.update(attrs)

    def render_js(self, field_id):
        ctype = ContentType.objects.get_for_model(self.model)
        return u"""$('#%s').autocomplete('%s',
                                         {max: 30,
                                         mustMatch: %s,
                                         minChars: %s});""" % (field_id,
                                                               reverse('form_widget_autocomplete',
                                                                       kwargs={'app': ctype.app_label,
                                                                               'model': ctype.model}),
                                                               str(self.mustmatch).lower(), 
                                                               self.chars)
    
    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        if value:
            final_attrs['value'] = escape(smart_unicode(value))
            
        if not self.attrs.has_key('id'):
            final_attrs['id'] = 'id_%s' % name
            
        return mark_safe('''<input type="text" %(attrs)s/> 
                <script type="text/javascript">
                %(js)s
                </script>''' % {'attrs': flatatt(final_attrs),
                                'js': self.render_js(final_attrs['id'])})
                