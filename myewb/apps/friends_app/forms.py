from django import forms
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from friends.models import *
from friends.importer import import_vcards
from friends.forms import UserForm

from messages.models import Message

# @@@ move to django-friends when ready

class ImportVCardForm(forms.Form):
    
    vcard_file = forms.FileField(label="vCard File")
    
    def save(self, user):
        imported, total = import_vcards(self.cleaned_data["vcard_file"].content, user)
        return imported, total
        
class InviteFriendForm(UserForm):
    
    to_user = forms.CharField(widget=forms.HiddenInput)
    message = forms.CharField(label="Message", required=False, widget=forms.Textarea(attrs = {'cols': '20', 'rows': '5'}))
    
    def clean_to_user(self):
        to_username = self.cleaned_data["to_user"]
        try:
            User.objects.get(username=to_username)
        except User.DoesNotExist:
            raise forms.ValidationError(u"Unknown user.")
            
        return self.cleaned_data["to_user"]
    
    def clean(self):
        to_user = User.objects.get(username=self.cleaned_data["to_user"])
        previous_invitations_to = FriendshipInvitation.objects.invitations(to_user=to_user, from_user=self.user)
        if previous_invitations_to.count() > 0:
            raise forms.ValidationError(u"Already requested friendship with %s" % to_user.visible_name())
        # check inverse
        previous_invitations_from = FriendshipInvitation.objects.invitations(to_user=self.user, from_user=to_user)
        if previous_invitations_from.count() > 0:
            raise forms.ValidationError(u"%s has already requested friendship with you" % to_user.visible_name())
        return self.cleaned_data
    
    def save(self):
        to_user = User.objects.get(username=self.cleaned_data["to_user"])
        message = self.cleaned_data["message"]
        invitation = FriendshipInvitation(from_user=self.user, to_user=to_user, message=message, status="2")
        invitation.save()
        if notification:
            notification.send([to_user], "friends_invite", {"invitation": invitation})
            notification.send([self.user], "friends_invite_sent", {"invitation": invitation})
        else:
            # TODO: templatize this
            # TODO: i18n this (trying to causes db errors right now)
            current_site = Site.objects.get_current()

            Message.objects.create(subject="Friendship request from %s" % self.user.visible_name(),
                                   body="You have received a friendship request from %s.<br/><br/>" % self.user.visible_name() +
                                   "<a href='http://%s%s'>click here to respond</a>" % (current_site, reverse('profile_detail', kwargs={'username': self.user.username})),
                                   sender=self.user,
                                   recipient=to_user)
                                   # sent_at is set automatically?
        self.user.message_set.create(message="Friendship requested with %s" % to_user.visible_name()) # @@@ make link like notification
        return invitation

