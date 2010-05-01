"""myEWB address-related forms

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

"""
import settings
from django import forms
from django.template.loader import render_to_string

class AddressWidget(forms.HiddenInput):
#    def __init__(self, *args, **kwargs):
#        self.user = kwargs.pop('user')
#        return super(AddressWidget, self).__init__(args, kwargs)

    is_hidden = False
    def render(self, name, value, attrs=None):
        field = super(AddressWidget, self).render(name, value, attrs)

        return render_to_string('profiles/address_widget.html',
                                {'field': field,
                                 'user': self.user,
                                 'STATIC_URL': settings.STATIC_URL})


class AddressField(forms.IntegerField):
    _user = None
    widget = AddressWidget

    def _get_user(self):
        if not self._user:
            address = self.form.initial.get(self.name, self.field.initial)
            self.user = address.content_object
        return self._user

    def _set_user(self, value):
        self._user = self.widget.user = value
    user = property(_get_user, _set_user)

    def __init__(self, *args, **kwargs):
        super(AddressField, self).__init__(*args, **kwargs)

