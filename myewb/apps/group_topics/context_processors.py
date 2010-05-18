"""myEWB post counts

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

from django.core.cache import cache
from group_topics.models import GroupTopic
from settings import CACHE_TIMEOUT

def newposts(request):
    """
    Adds the number of new posts & replies since last signin
    """
    user = request.user
    
    postcount = 0
    replycount = 0
    
    if user.is_authenticated():
        
        cache_key = "newpostcount%s%s" % (user.username, user.get_profile().adminovision)
        counts = cache.get(cache_key)
        
        if counts is None:
            lastlogin = user.get_profile().previous_login
        
            if lastlogin:
                posts = GroupTopic.objects.since(lastlogin, user=user)
                postcount = posts.count()
    
                replies = GroupTopic.objects.replies_since(lastlogin, user=user)
                replycount = replies.count()
            else:
                postcount = 0
                replycount = 0
                
            cache.set(cache_key, (postcount, replycount), CACHE_TIMEOUT)
        else:
            postcount, replycount = counts
                

    ctx = {"posts_since_login": postcount,
           "replies_since_login": replycount}
    return ctx
