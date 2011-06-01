from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.fields import email_re

from base_groups.models import BaseGroup

urlpatterns = patterns('legacy_urls.actions',
    url(r'^ModifyListMembership/(?P<group_id>\d+)$', 'modify_list_membership'),
    url(r'^ModifyListMembership/(?P<group_slug>[\w\._\-]+)$', 'modify_list_membership_slug'),
    url(r'^DoSilentMainListSignup/(?P<email>[\.\-_@:\+\w]+)$', 'silent_signup'),
    )

def modify_list_membership_slug(request, group_slug):
    grp = get_object_or_404(BaseGroup, slug=group_slug)
    return modify_list_membership(request, grp.pk, group=grp)

def modify_list_membership(request, group_id, group=None):
    action = request.POST.get("ActionType", None)
    redirect = request.POST.get("Redirect", None)
    emails = request.POST.get("Emails", None)
    
    if group == None:
        group = get_object_or_404(BaseGroup, id=group_id)
    
    if group.slug != "ewb" and group.visibility != 'E':
        return render_to_response('denied.html', context_instance=RequestContext(request))
    
    if action and action == "add" and emails:
        email_list = emails.split()   # splits by whitespace characters
        
        for email in email_list:
            if email_re.search(email):
                if group.slug == "ewb":
                    User.extras.create_bulk_user(email)
                else:
                    group.add_email(email)

    if redirect:
        return HttpResponseRedirect(redirect)
    else:
        return HttpResponseRedirect(reverse("home"))

def silent_signup(request, email):
    if email_re.search(email):
        User.extras.create_bulk_user(email)
        
    return HttpResponse("") 
