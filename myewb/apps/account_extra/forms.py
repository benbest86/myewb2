from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ugettext

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from emailconfirmation.models import EmailAddress

class EmailLoginForm(forms.Form):
    # login_name may be either the username or an associated email address
    login_name = forms.CharField(label = _("Email"), max_length=75, required=True, widget=forms.TextInput())
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(render_value=False))
    remember = forms.BooleanField(label=_("Remember Me"), help_text=_("If checked you will stay logged in for 3 weeks"), required=False)
    
    user = None

    def clean(self):
        if self._errors:
            return
            
        login_name = self.cleaned_data["login_name"]
        username = None
        
        # first, check if there's a username matching the associated login_name
        # usernames can only contain letters, numbers, and underscores (not dots or @s) so no possibility of conflict
        if User.objects.filter(username=login_name).count() > 0:
            username = login_name
        else:        
            possible_users = [address.user for address in EmailAddress.objects.filter(email=login_name)] # verification not required
        
            # TODO: What happens if there are more than one user with a given address? (shouldn't be!)        
            if len(possible_users) > 0:
                possible_user = possible_users[0]
            else:
                raise forms.ValidationError(_("The login credentials you specified are not correct."))        
        
            username = possible_user.username
            
        user = authenticate(username=username, password=self.cleaned_data["password"])
        if user:
            if user.is_active:
                self.user = user
            else:
                raise forms.ValidationError(_("This account is currently inactive."))
        else:
            raise forms.ValidationError(_("The login credentials you specified are not correct."))
        return self.cleaned_data

    def login(self, request):
        if self.is_valid():
            login(request, self.user)
            if self.user.first_name and self.user.last_name:
                login_message=ugettext(u"Successfully logged in. Welcome, %(first_name)s %(last_name)s.") % {
                    'first_name': self.user.first_name,
                    'last_name': self.user.last_name
                }
            else:
                login_message=ugettext(u"Successfully logged in.")
            request.user.message_set.create(message=login_message)
            if self.cleaned_data['remember']:
                request.session.set_expiry(60 * 60 * 24 * 7 * 3)
            else:
                request.session.set_expiry(0)
            return True
        return False
        
class EmailSignupForm(forms.Form):

    email = forms.EmailField(label = _("Email"), required = True, widget = forms.TextInput())
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput(render_value=False))

    confirmation_key = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput())
    
    def clean_email(self):
        try:
            user = User.objects.get(email__iexact=self.cleaned_data["email"])
        except User.DoesNotExist:
            return self.cleaned_data["email"]
        
        memberships = user.member_groups.all()
        for membership in memberships:
            if membership.is_bulk():
                return self.cleaned_data["email"]       # we'll temporarily allow the duplicate
        
        # else...        
        raise forms.ValidationError(_("This email address has already been used. Please use another."))

    def clean(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data

    def save(self):
        # username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password1"]
        
        username = User.objects.make_random_password()     # not a password per se, just a random string
        while User.objects.filter(username=username).count() > 0:   # ensure uniqueness
            username = User.objects.make_random_password()

        if self.cleaned_data["confirmation_key"]:
            from friends.models import JoinInvitation # @@@ temporary fix for issue 93 (-- Pinax comment)
            try:
                join_invitation = JoinInvitation.objects.get(confirmation_key = self.cleaned_data["confirmation_key"])
                confirmed = True
            except JoinInvitation.DoesNotExist:
                confirmed = False
        else:
            confirmed = False

        # @@@ clean up some of the repetition below -- DRY! (-- Pinax comment)

        if confirmed:
            if email == join_invitation.contact.email:
                new_user = User.objects.create_user(username, email, password)
                join_invitation.accept(new_user) # should go before creation of EmailAddress below
                new_user.message_set.create(message=ugettext(u"Your email address has already been verified"))
                # already verified so can just create
                EmailAddress(user=new_user, email=email, verified=True, primary=True).save()
            else:
                new_user = User.objects.create_user(username, email, password)      # supply email - change from Pinax
                join_invitation.accept(new_user) # should go before creation of EmailAddress below
                if email:
                    new_user.message_set.create(message=ugettext(u"Confirmation email sent to %(email)s") % {'email': email})
                    EmailAddress.objects.add_email(new_user, email)
        else:
            new_user = User.objects.create_user(username, email, password)      # supply email - change from Pinax
            if email:
                new_user.message_set.create(message=ugettext(u"Confirmation email sent to %(email)s") % {'email': email})
                EmailAddress.objects.add_email(new_user, email)

        if settings.ACCOUNT_EMAIL_VERIFICATION:
            new_user.is_active = False
            new_user.save()

        return username, password # required for authenticate()