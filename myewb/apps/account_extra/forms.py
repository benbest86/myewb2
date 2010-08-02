from datetime import datetime, timedelta, date

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _, ugettext
from django.shortcuts import get_object_or_404

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from account_extra import signals
from emailconfirmation.models import EmailAddress
from networks.models import Network
from siteutils import online_middleware

class EmailLoginForm(forms.Form):
    # login_name may be either the username or an associated email address
    login_name = forms.CharField(label = _("Email"), max_length=75, required=True, widget=forms.TextInput())
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(render_value=False))
    remember = forms.BooleanField(label=_("Remember Me"), help_text=_("<label class=\"remember-me-label\" for=\"id_remember\">Remember me for 3 weeks</label>"), required=False)
    
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
            try:
                email = EmailAddress.objects.get(email=login_name, verified=True)
            except EmailAddress.DoesNotExist:
                if EmailAddress.objects.filter(email=login_name):
                    raise forms.ValidationError(_("Your email address must be confirmed in order to log in."))
                else:
                    raise forms.ValidationError(_("The login credentials you specified are not correct."))        
            except EmailAddress.MultipleObjectsReturned:
                raise forms.ValidationError(_("An error has occurred and there are two registered users for this address. Please contact network admin to resolve the problem."))        

            # possible_users = [address.user for address in EmailAddress.objects.filter(email=login_name)] # verification not required
        
            # TODO: What happens if there are more than one user with a given address? (shouldn't be!)        
            # if len(possible_users) > 0:
            #     possible_user = possible_users[0]
            # else:
            #     raise forms.ValidationError(_("The login credentials you specified are not correct."))        
            username = email.user.username
        
            # username = possible_user.username
            
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
            online_middleware.remove_user(request)
            login(request, self.user)
            
            # prompt to change password if too simple
            if self.user.google_username and not self.user.google_sync:
                self.user.message_set.create(message="<b>Your password is too simple - you must change it before signing into your @ewb.ca email account<br/> \
                <a href='" + reverse('acct_passwd') + "'>click here to change your password</a></b>")
            
            # update stats
            self.user.get_profile().login_count += 1
            
            if self.user.get_profile().current_login == None:
                self.user.get_profile().previous_login = datetime.now()
            else:
                self.user.get_profile().previous_login = self.user.get_profile().current_login
            
            self.user.get_profile().current_login = datetime.now()
            self.user.get_profile().save()
            
            # set message
            login_message=ugettext(u"Welcome back, %(name)s") % {
                'name': self.user.visible_name()
            }
            request.user.message_set.create(message=login_message)
            if self.cleaned_data['remember']:
                request.session.set_expiry(60 * 60 * 24 * 7 * 3)
            else:
                request.session.set_expiry(0)
                
            # set account reminder messages
            # (should this be done somewhere else, probably profiles app, with a signal listener?)
            membership_expiry = self.user.get_profile().membership_expiry
            if membership_expiry:
                if date.today() + timedelta(days=7) > membership_expiry:
                    request.user.message_set.create(message="Your membership expires within a week.<br/><a href='%s'>Renew it now!</a>" % reverse('profile_pay_membership', kwargs={'username': request.user.username}))
                elif date.today() + timedelta(days=30) > membership_expiry:
                    request.user.message_set.create(message="Your membership expires within a month.<br/><a href='%s'>Renew it now!</a>" % reverse('profile_pay_membership', kwargs={'username': request.user.username}))
                
            signals.signin.send(sender=self.user, user=self.user)
            return True
        return False
        
class EmailSignupForm(forms.Form):

    firstname = forms.CharField(label=_("First name"))
    lastname = forms.CharField(label=_("Last name"))
    email = forms.EmailField(label = _("Email"), required = True, widget = forms.TextInput())
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput(render_value=False))
    chapter = forms.ChoiceField(choices=[('none', _('none'))], required=False)

    confirmation_key = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        #chapterlist = kwargs.pop('chapters', None)
        
        chapterlist = Network.objects.filter(chapter_info__isnull=False, is_active=True).order_by('name')
        for chapter in chapterlist:
            #try:
            #    i = self.base_fields['chapter'].choices.index((chapter.slug, chapter.chapter_info.chapter_name))
            #except ValueError:
            #    self.base_fields['chapter'].choices.append((chapter.slug, chapter.chapter_info.chapter_name))
            self.base_fields['chapter'].choices.append((chapter.slug, chapter.chapter_info.chapter_name))
        
        self.base_fields['chapter'].initial = kwargs.pop('chapter', None)

        super(EmailSignupForm, self).__init__(*args, **kwargs)
        
    def clean_email(self):
        other_emails = EmailAddress.objects.filter(email__iexact=self.cleaned_data['email'])
        verified_emails = other_emails.filter(verified=True)
        if verified_emails.count() > 0:
            raise forms.ValidationError(_("This email address has already been used. Please use another."))
        if other_emails.count() > 0:
            raise forms.ValidationError(_("This email is already awaiting confirmation. Click here TODO to send another confirmation email."))
        
        return self.cleaned_data['email']

    def clean(self):
        # XXX shouldn't this be more like the below???
        # password1 = self.cleaned_data.get('password1', None)
        # password2 = self.cleaned_data.get('password2', None)
        # if password1 is None or password2 is None or password1 != password2:
        #     raise forms.ValidationError(_("You must type the same password each time."))

        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data

    def save(self):
        # username = self.cleaned_data["username"]
        firstname = self.cleaned_data['firstname']
        lastname = self.cleaned_data['lastname']
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

        add_email = None
        if confirmed:
            if email == join_invitation.contact.email:
                new_user = User.objects.create_user(username, email, password)
                join_invitation.accept(new_user) # should go before creation of EmailAddress below
                new_user.message_set.create(message=ugettext(u"Your email address has already been verified"))
                # already verified so can just create
                EmailAddress(user=new_user, email=email, verified=True, primary=True).save()
            else:
                new_user = User.objects.create_user(username, "", password)      
                join_invitation.accept(new_user) # should go before creation of EmailAddress below
                if email:
                    new_user.message_set.create(message=ugettext(u"Confirmation email sent to %(email)s") % {'email': email})
                    add_email = email
        else:
            try:
                new_user = User.objects.get(email=email, is_bulk=True)
                signals.listupgrade.send(sender=new_user, user=new_user)
            except User.DoesNotExist:
                new_user = User.objects.create_user(username, "", password)
                signals.signup.send(sender=new_user, user=new_user)      
            
            if email:
                # new_user.message_set.create(message=ugettext(u"Confirmation email sent to %(email)s") % {'email': email})
                add_email = email
        profile = new_user.get_profile()
        profile.first_name = firstname
        profile.last_name = lastname
        profile.save()
        
        new_user.first_name = firstname
        new_user.last_name = lastname

        if settings.ACCOUNT_EMAIL_VERIFICATION:
            new_user.is_active = False
        
        new_user.save()
        
        # needs to be moved down after user is saved, so that the email 
        # confirmation message has the peron's actual name in it 
        if add_email:
            EmailAddress.objects.add_email(new_user, add_email)
        
        if self.cleaned_data['chapter'] != "none" and self.cleaned_data['chapter'] != "":
            chapter = get_object_or_404(Network, slug=self.cleaned_data['chapter'])
            chapter.add_member(new_user)
            
        return username, password # required for authenticate()

