import settings
from group_topics.models import GroupTopic

def myewb_settings(request):
    gt = GroupTopic.objects.all().order_by('-last_reply')[:1]
    
    return {'CACHE_TIMEOUT': settings.CACHE_TIMEOUT,
            'LATEST_POST': gt[0].last_reply}
    