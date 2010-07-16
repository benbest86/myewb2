"""myEWB APS applications

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext_lazy as _

from volunteering.models import Session
from volunteering.forms import SessionForm

@permission_required('overseas')
def sessions(request):
    sessions = Session.objects.all()

    return render_to_response('volunteering/session/list.html', {
        "session_list": sessions,
    }, context_instance=RequestContext(request))

def session_detail(request, object_id):
    session = get_object_or_404(Session, id=object_id)
    
    return render_to_response('volunteering/session/detail.html',
                              {'session': session},
                              context_instance=RequestContext(request))

def session_edit(request, object_id=None):
    if object_id:
        session = get_object_or_404(Session, id=object_id)
    else:
        session = None
        
    if request.method == 'POST':
        if session:
            form = SessionForm(request.POST, instance=session)
        else:
            form = SessionForm(request.POST)
            
        if form.is_valid():
            session = form.save()
            return render_to_response('volunteering/session/detail.html',
                                      {'session': session,
                                       'form': form},
                                       context_instance=RequestContext(request))
        
        return render_to_response('volunteering/session/form.html',
                                  {'session': session,
                                   'form': form},
                                   context_instance=RequestContext(request))
    else:
        if session:
            form = SessionForm(instance=session)
        else:
            form = SessionForm()
    
        #return render_to_response('volunteering/session_detail.html',
        return render_to_response('volunteering/session/form.html',
                                  {'session': session,
                                   'form': form},
                                   context_instance=RequestContext(request))
