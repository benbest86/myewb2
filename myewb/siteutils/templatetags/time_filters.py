import datetime
from django import template
from django.template.defaultfilters import stringfilter, date, time, timesince

register = template.Library()

# adapted from django's built-in timesince filter
@register.filter
#@stringfilter
def since(d):
    if not d:
        return u''
    
    if not isinstance(d, datetime.datetime) and not isinstance(d, datetime.date):
        return u''
    
    # within the past 12 hours, present it as an hour offset
    if d > (datetime.datetime.now() - datetime.timedelta(seconds=43200)):
        delta = datetime.datetime.now() - d     # find the time difference
        hours = delta.seconds / 3600
        minutes = (delta.seconds - (hours * 3600)) / 60
        
        print "hours:", hours
        print "minutes:", minutes
        print "originally", d
        print ""
        
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
        return "today at %s" % time(d)
    elif d.date() == (datetime.date.today() - datetime.timedelta(1)):
        return "yesterday at %s" % time(d)
    else:
        return "on %s at %s" % (date(d), time(d))
