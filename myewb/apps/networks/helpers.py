from django.http import HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.contrib.auth.models import User
from base_groups.models import BaseGroup, GroupMember
from networks.models import Network

def is_exec_over(subject, user):
    """
    Checks to see if "user" is an exec of a chapter that "subject" is in.
    
    Assumptions:
    - you can only be an exec member of one chapter
    - all networks are chapters
    - admins are always considered execs
    """
    # admins always have access
    # FIXME: probably sholdn't use is_superuser or is_staff here...
    if user.is_superuser or user.is_staff:
        return True

    # and guests never have access
    if not subject.is_authenticated() or not user.is_authenticated():
        return False
    
    # find all networks that i am an exec of...
    groups = Network.objects.filter(members__user=user,
                                    members__is_admin=True)
    
    # not an exec? good bye =)
    if groups.count() == 0:
        return False
    
    # see if the subject is a member of any of my exec chapters
    membership = GroupMember.objects.filter(user=subject,
                                            group__in=groups)
    
    if membership.count() > 0:
        return True
    else:
        return False
    