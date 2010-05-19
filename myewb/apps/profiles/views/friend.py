"""myEWB profile friend views

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

import random, sha
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from profiles.forms import StudentRecordForm, WorkRecordForm, MembershipForm, PhoneNumberForm, SettingsForm

from friends.models import Friendship, FriendshipInvitation

def list(request, username):
    other_user = get_object_or_404(User, username=username)
    friends = Friendship.objects.friends_for_user(other_user)
    
    return render_to_response("profiles/friend_list.html",
                              {"other_user": other_user,
                               "friends": friends,
                              },
                              context_instance=RequestContext(request))
    
def requests(request, username):
    other_user = get_object_or_404(User, username=username)
    requests = FriendshipInvitation.objects.filter(to_user=other_user, status=2)
    
    return render_to_response("profiles/friend_requests.html", 
                              {"other_user": other_user,
                               "requests": requests,
                              },
                              context_instance=RequestContext(request))
