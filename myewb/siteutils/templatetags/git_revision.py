from django import template
#from django.conf import settings
#from django.core.cache import cache
#from django.utils.encoding import smart_str
#from os.path import abspath
#from os.path import dirname as dn
#from django.utils.version import get_svn_revision
#from django.db.models.loading import get_app
import subprocess
import settings

register = template.Library()

# cache values
gdate = None
grev = None

# thanks http://www.djangosnippets.org/snippets/1777/
@register.simple_tag
def git_date():
    global gdate
    
    if gdate == None:
        _proc = subprocess.Popen('git log --no-color -n 1',
                                 shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 cwd=settings.PROJECT_ROOT)
        try:
            gdate = [x.split('Date:')[1].strip() for x in
                     _proc.communicate()[0].splitlines() if x.startswith('Date:')][0]
            datearray = gdate.split(' ')
            gdate = "%s %s, %s" % (datearray[1], datearray[2], datearray[4])

        except IndexError:
            gdate = 'unknown'
        
    return gdate

@register.simple_tag
def git_rev():
    global grev
    
    if grev == None:
        _proc = subprocess.Popen('git log --no-color -n 1',
                                 shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 cwd=settings.PROJECT_ROOT)
        try:
            grev = [x.split('commit')[1].strip() for x in
                    _proc.communicate()[0].splitlines() if x.startswith('commit')][0]
        except IndexError:
            grev = 'unknown'

    return grev

