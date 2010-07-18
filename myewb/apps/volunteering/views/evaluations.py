"""myEWB APS applications

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

from copy import copy

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext_lazy as _

from volunteering.models import Session, Question, EvaluationCriterion, Evaluation, Application
from volunteering.forms import SessionForm, QuestionForm, EvaluationCriterionForm

@permission_required('overseas')
def evaluation_list(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    
    complete = session.complete_applications()
    draft = session.draft_applications()
    
    return render_to_response('volunteering/evaluation/list.html',
                              {'session': session,
                               'complete': complete,
                               'draft': draft},
                              context_instance=RequestContext(request)) 

@permission_required('overseas')
def evaluation_detail(request, app_id):
    application = get_object_or_404(Application, id=app_id)
    evaluation = Evaluation.objects.get_or_create(application=application)

    return render_to_response('volunteering/evaluation/detail.html',
                              {'evaluation': evaluation,
                               'application': application
                              },
                              context_instance=RequestContext(request))

