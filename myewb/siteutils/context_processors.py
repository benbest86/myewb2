from time import time
import settings
from group_topics.models import GroupTopic

def myewb_settings(request):
    gt = GroupTopic.objects.all().order_by('-last_reply')[:1]
    try:
        latest_post = gt[0].last_reply
    except:
        latest_post = 0

    grandfathered = False
    cache_stamp = 0
    if request.user.is_authenticated():
        grandfathered = request.user.get_profile().grandfathered
        request.user.get_profile().grandfathered = False
        request.user.get_profile().messages_as_emails = True
        request.user.get_profile().save()
        
        if request.session.get("cache_stamp", None):
            cache_stamp = request.session['cache_stamp']
    
    return {'CACHE_TIMEOUT': settings.CACHE_TIMEOUT,
            'LATEST_POST': latest_post,
            'CACHE_STAMP': cache_stamp,
            'grandfathered': grandfathered}
