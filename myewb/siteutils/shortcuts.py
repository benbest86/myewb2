"""myEWB shortcuts

This file is part of myEWB
Copyright 20109 Engineers Without Borders Canada

@author: Francis Kung
"""

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import _get_queryset
from django.views.generic.simple import redirect_to

def get_object_or_none(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None

# does the same thing as django.views.generic.simple.redirect_to, except instead
# of taking a URL, it takes a named URL that it passes through django's reverse().
# note it does NOT support the query_string parameter
def redirect_to_reverse(request, url, permanent=False, **kwargs):
    if permanent:
        return HttpResponsePermanentRedirect(reverse(url))
    else:
        return HttpResponseRedirect(reverse(url))
