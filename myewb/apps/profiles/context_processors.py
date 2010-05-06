"""myEWB toolbar states

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

from profiles.models import ToolbarState
from siteutils.shortcuts import get_object_or_none

def toolbar_states(request):
    user = request.user
    
    closed = []
    
    if user.is_authenticated():
        # wrapped "get" since this needs sample data to be loaded
        states = ToolbarState.objects.filter(user=user,
                                             state='c')
        for s in states:
            closed.append(s.toolbar) 
        
    return {'closed_toolbars': closed}
