from time import time
from datetime import datetime
import settings
from group_topics.models import GroupTopic
from pytz import country_timezones, common_timezones, timezone as pytzone
from siteutils.templatetags.time_filters import timezones, tznames

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
        if grandfathered:
            request.user.get_profile().grandfathered = False
            request.user.get_profile().messages_as_emails = True
            request.user.get_profile().save()
        
        if request.session.get("cache_stamp", None):
            cache_stamp = request.session['cache_stamp']
    
    return {'CACHE_TIMEOUT': settings.TEMPLATE_CACHE_TIMEOUT,
            'LATEST_POST': latest_post,
            'CACHE_STAMP': cache_stamp,
            'grandfathered': grandfathered}

def timezone(request):
    current_timezone = None
    detected_timezone = request.session.get("detected_timezone", None)

    if request.session.get("timezone", None):
        current_timezone = request.session['timezone']

    if request.user.is_authenticated() and request.user.get_profile().timezone:
        if current_timezone != request.user.get_profile().timezone:
            request.user.get_profile().timezone = current_timezone
            request.user.get_profile().save()
            
    if request.GET.get("tzoffset", None):
        offset = 0 - int(request.GET['tzoffset'])
        tz = None
        
        for name, code in tznames.items():
            zoneoffset = pytzone(code).utcoffset(datetime.now()).seconds
            if zoneoffset > 43200:          # over 12 hours: need to wrap arond
                zoneoffset = zoneoffset - 86400        # 24 hours * 60 minutes * 60 seconds
            zoneoffset = zoneoffset / 60        # seconds to minutes
            if zoneoffset == offset:
                tz = name
                break

        if not tz:
            offset = int(offset) / -60
            if offset > 0:
                tz = 'Etc/GMT+%s' % offset
            elif offset < 0:
                tz = 'Etc/GMT%s' % offset
            else:
                tz = 'UTC'
            
        request.session['detected_timezone'] = tz
        if not current_timezone:
            request.session['timezone'] = tz
            current_timezone = tz
        
    return {'current_timezone': current_timezone,
            'detected_timezone': detected_timezone,
            'timezones': timezones}

