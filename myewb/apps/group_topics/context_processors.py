"""myEWB post counts

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

from group_topics.models import GroupTopic

def newposts(request):
    """
    Adds the number of new posts since last signin
    """
    user = request.user
    lastlogin = user.get_profile().previous_login
    
    posts = GroupTopic.objects.since(lastlogin, user=user)

    ctx = {"posts_since_login": posts.count()}
    return ctx
