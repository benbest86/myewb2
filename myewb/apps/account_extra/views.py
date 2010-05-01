import re
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound, HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import logout as pinaxlogout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms import fields
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext_lazy as _

from account.utils import get_default_redirect
from emailconfirmation.models import EmailAddress, EmailConfirmation

from account_extra.forms import EmailLoginForm, EmailSignupForm
from account.views import login as pinaxlogin
from account.views import signup as pinaxsignup
from account.forms import AddEmailForm
from base_groups.models import LogisticalGroup

from siteutils import online_middleware

def login(request, form_class=EmailLoginForm, 
        template_name="account/login.html", success_url=None,
        associate_openid=False, openid_success_url=None, url_required=False):
    return pinaxlogin(request, form_class, template_name, success_url, 
            associate_openid, openid_success_url, url_required)

def signup(request, form_class=EmailSignupForm,
        template_name="account/signup.html", success_url=None):
    if success_url is None:
        success_url = get_default_redirect(request)
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            username, password = form.save()
            if settings.ACCOUNT_EMAIL_VERIFICATION:
                return render_to_response("account/verification_sent.html", {
                    "email": form.cleaned_data["email"],
                }, context_instance=RequestContext(request))
            else:
                user = authenticate(username=username, password=password)
                auth_login(request, user)
                
                login_message=ugettext(u"Welcome back, %(name)s") % {
                    'name': user.visible_name
                }
                request.user.message_set.create(message=login_message)
                return HttpResponseRedirect(success_url)
    else:
        form = form_class()
    return render_to_response(template_name, {
        "form": form,
    }, context_instance=RequestContext(request))
    
def logout(request):
    online_middleware.remove_user(request)
    return pinaxlogout(request, template_name="account/logout.html")

@login_required
def email(request, form_class=AddEmailForm, template_name="account/email.html",
          username=None):
    
    if username:
        if not request.user.has_module_perms("profiles"):
            return HttpResponseForbidden()
        else:
            user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    if request.method == "POST" and request.user.is_authenticated():
        if request.POST["action"] == "add":
            add_email_form = form_class(user, request.POST)
            if add_email_form.is_valid():
                add_email_form.save()
                add_email_form = form_class() # @@@
        else:
            add_email_form = form_class(user)
            if request.POST["action"] == "send":
                email = request.POST["email"]
                try:
                    email_address = EmailAddress.objects.get(
                        user=user,
                        email=email,
                    )
                    request.user.message_set.create(
                        message=_("Confirmation email sent to %(email)s") % {
                            'email': email,
                        })
                    EmailConfirmation.objects.send_confirmation(email_address)
                except EmailAddress.DoesNotExist:
                    pass
            elif request.POST["action"] == "remove":
                email = request.POST["email"]
                try:
                    email_address = EmailAddress.objects.get(
                        user=user,
                        email=email
                    )
                    email_address.delete()
                    request.user.message_set.create(
                        message=_("Removed email address %(email)s") % {
                            'email': email,
                        })
                except EmailAddress.DoesNotExist:
                    pass
            elif request.POST["action"] == "primary":
                email = request.POST["email"]
                email_address = EmailAddress.objects.get(
                    user=user,
                    email=email,
                )
                email_address.set_as_primary()
    else:
        add_email_form = form_class()
    return render_to_response(template_name, {
        "add_email_form": add_email_form,
        "other_user": user,
    }, context_instance=RequestContext(request))

def silent_signup(request, email):
    regex = re.compile(fields.email_re)
    if not regex.search(email):
        return HttpResponseNotFound()   # invalid email

    group = get_object_or_404(LogisticalGroup, slug="silent_signup_api")
    group.add_email(email)
    return HttpResponse("success")
