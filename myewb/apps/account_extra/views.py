from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import logout as pinaxlogout
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext_lazy as _

from account.utils import get_default_redirect

from account_extra.forms import EmailLoginForm, EmailSignupForm
from account.views import login as pinaxlogin
from account.views import signup as pinaxsignup

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
                
                if user.first_name and user.last_name:
                    login_message=ugettext(u"Successfully logged in. Welcome, %(first_name)s %(last_name)s.") % {
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                else:
                    login_message=ugettext(u"Successfully logged in.")
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