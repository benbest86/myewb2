"""myEWB post counts

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

from group_topics.models import GroupTopic

def newposts(request):
    """
    Adds the number of new posts & replies since last signin
    """
    user = request.user
    
    if user.is_authenticated():
        lastlogin = user.get_profile().previous_login
    
        posts = GroupTopic.objects.since(lastlogin, user=user)
        postcount = posts.count()

        replies = GroupTopic.objects.replies_since(lastlogin, user=user)
        replycount = replies.count()
    else:
        postcount = 0
        replycount = 0

    ctx = {"posts_since_login": postcount,
           "replies_since_login": replycount}
    return ctx
