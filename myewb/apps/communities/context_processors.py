"""myEWB post counts

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

from communities.models import Community
from siteutils.shortcuts import get_object_or_none

def is_exec(request):
    """
    Sets a flag for whether a user is a chapter exec member
    """
    user = request.user
    
    if user.is_staff:
        return {'is_exec': True}
    
    ctx = {'is_exec': False}
    
    if user.is_authenticated():
        # wrapped "get" since this needs sample data to be loaded 
        execlist = get_object_or_none(Community, slug='exec')
        
        if execlist and execlist.user_is_member(user):
            ctx['is_exec'] = True

    return ctx

    # TODO: implement some kind of caching?