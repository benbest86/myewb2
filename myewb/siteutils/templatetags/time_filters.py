import datetime, time, os
from django import template
from django.template import defaultfilters
from pytz import FixedOffset, timezone
import pytz
import settings

register = template.Library()
            
timezones = [
 'Canada/Atlantic',
 'Canada/Central',
 'Canada/Eastern',
 'Canada/Mountain',
 'Canada/Newfoundland',
 'Canada/Pacific',
 'Burkina Faso',
 'Ghana',
 'Malawi',
 'Zambia',
]

tznames = {'Canada/Atlantic': 'America/Halifax',
           'Canada/Central': 'America/Winnipeg', 
           'Canada/Eastern': 'America/Toronto',
           'Canada/Mountain': 'America/Edmonton',
           'Canada/Newfoundland': 'America/St_Johns',
           'Canada/Pacific': 'America/Vancouver',
           'Burkina Faso': 'Africa/Accra',
           'Ghana': 'Africa/Accra',
           'Malawi': 'Africa/Lusaka',
           'Zambia': 'Africa/Lusaka',
          }

# adapted from django's built-in timesince filter
class MktimeNode(template.Node):
    def __init__(self, d):
        self.d = template.Variable(d)
        
    def render(self, context):
        # get necessary variables
        d = self.d.resolve(context)
        request = template.Variable('request').resolve(context)

        # something's inconsistent... bail!
        if not d:
            return u''
        
        if not isinstance(d, datetime.datetime) and not isinstance(d, datetime.date):
            return u''

        # find the user's timezone - either through their profile or session variable 
        tzone = None
        if request.user.is_authenticated():
            tzone = request.user.get_profile().timezone
        
        if not tzone:
            tzone = request.session.get("timezone", None)
            
        # modify the date to match the new timezone 
        if tzone and isinstance(d, datetime.datetime):
            # I use some non-conventional names... fix them here:
            if tznames.get(tzone, None):
                tzone = tznames[tzone]

            # and do the match.
            tzone = timezone(tzone)
            current_offset = timezone(settings.TIME_ZONE).utcoffset(d)
            new_offset = tzone.utcoffset(d)
            
            if current_offset != new_offset:
                delta = new_offset - current_offset
                d = d + delta
            
        # within the past 12 hours, present it as an hour offset
        if d > (datetime.datetime.now() - datetime.timedelta(seconds=43200)):
            delta = datetime.datetime.now() - d     # find the time difference
            hours = delta.seconds / 3600
            minutes = (delta.seconds - (hours * 3600)) / 60
        
            # round to the nearest hour =)
            if minutes > 30:
                hours = hours + 1
            
            if hours > 1:
                return ", %s hours ago" % hours
            elif hours == 1:
                return ", 1 hour ago"
            elif minutes < 5:
                return ", just now"
            else:
                return ", %s minutes ago" % minutes
        
        # otherwise do the full date/time
        elif d.date() == datetime.date.today():
            return "today at %s" % defaultfilters.time(d)
        elif d.date() == (datetime.date.today() - datetime.timedelta(1)):
            return "yesterday at %s" % defaultfilters.time(d)
        else:
            return "on %s at %s" % (defaultfilters.date(d), defaultfilters.time(d))

@register.tag
def mktime(parser, token):
    try:
        tag_name, d = token.split_contents()
    except:
        raise template.TemplateSyntaxError, "mis-formed mktime call"
    return MktimeNode(d)
