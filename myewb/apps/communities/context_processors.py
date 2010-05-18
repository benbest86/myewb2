"""myEWB post counts

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

from django.core.cache import cache
from communities.models import Community
from siteutils.shortcuts import get_object_or_none

def is_exec(request):
    """
    Sets a flag for whether a user is a chapter exec member
    """
    user = request.user
    
    if user.is_staff or user.is_superuser:
        return {'is_exec': True}
    
    ctx = {'is_exec': False}
    
    if user.is_authenticated():
        cache_key = "is_exec_%s" % user.username
        is_exec = cache.get(cache_key)
        if is_exec is None:
            # wrapped "get" since this needs sample data to be loaded 
            execlist = get_object_or_none(Community, slug='exec')
            
            if execlist and execlist.user_is_member(user):
                is_exec = True
            else:
                is_exec = False
            cache.set(cache_key, is_exec, 5*60)

        ctx['is_exec'] = is_exec
    return ctx
