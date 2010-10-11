"""myEWB APS applications

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

from copy import copy
from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext_lazy as _

from mailer import send_mail
from siteutils.shortcuts import get_object_or_none
from volunteering.models import Session, EvaluationCriterion, Evaluation, Application, EvaluationComment, EvaluationResponse, InterviewQuestion, Answer
from volunteering.forms import SessionForm, EvaluationCriterionForm, EmailForm

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
    evaluation, created = Evaluation.objects.get_or_create(application=application)
    
    return render_to_response('volunteering/evaluation/detail.html',
                              {'evaluation': evaluation,
                               'application': application,
                               'is_me': False
                              },
                              context_instance=RequestContext(request))

@permission_required('overseas')
def evaluation_comment(request, app_id):
    application = get_object_or_404(Application, id=app_id)
    
    if request.method == 'POST':
        if request.POST.get('key', None):
            key = request.POST.get('key', None)
            comment = request.POST.get('comment', None)
        
            if comment:
                evalcomment, created = EvaluationComment.objects.get_or_create(evaluation=application.evaluation,
                                                                               key=key)
                evalcomment.comment = comment
                evalcomment.save()
            else:
                comment = get_object_or_none(EvaluationComment,
                                             evaluation=application.evaluation,
                                             key=key)
                if comment:
                    comment.delete()
            return HttpResponse("success")
    elif request.is_ajax():
        comments = EvaluationComment.objects.filter(evaluation=application.evaluation)
        json = serializers.get_serializer('json')()
        response = HttpResponse(mimetype='application/json')
        json.serialize(comments, stream=response)
        return response
    return HttpResponse("invalid")

@permission_required('overseas')
def evaluation_interview_answer(request, app_id):
    application = get_object_or_404(Application, id=app_id)
    
    if request.method == 'POST':
        if request.POST.get('key', None):
            key = request.POST.get('key', None)
            question = get_object_or_404(InterviewQuestion, id=key, session=application.session)
            comment = request.POST.get('comment', None)
        
            if comment:
                answer, created = Answer.objects.get_or_create(application=application,
                                                               question=question)
                answer.answer = comment
                answer.save()
            else:
                answer = get_object_or_none(Answer,
                                            application=application,
                                            question=question)
                if answer:
                    answer.delete()
            return HttpResponse("success")
    elif request.is_ajax():
        answers = Answer.objects.filter(application=application)
        json = serializers.get_serializer('json')()
        response = HttpResponse(mimetype='application/json')
        json.serialize(comments, stream=response)
        return response
    return HttpResponse("invalid")

@permission_required('overseas')
def evaluation_criteria(request, app_id, criteria_id):
    application = get_object_or_404(Application, id=app_id)
    criteria = get_object_or_404(EvaluationCriterion, id=criteria_id, session=application.session)
    
    if request.method == 'POST':
        value = request.POST.get('value', None)
        
        response, created = EvaluationResponse.objects.get_or_create(evaluation=application.evaluation,
                                                                     evaluation_criterion=criteria)
        try:
            if value:
                response.response = value.strip()
                response.save()
                return HttpResponse(response.response)
        except:
            pass
    return HttpResponse("invalid")

@permission_required('overseas')
def evaluation_bulkedit(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    
    if request.method != 'POST':
        return HttpResponseForbidden()
    
    action = request.POST.get('action', None)
    app_id = []
    for field in request.POST:
        if field[0:4] == 'app-':
            try:
                app_id.append(int(field[4:]))
            except:
                pass
    applications = Application.objects.filter(id__in=app_id, session=session)

    if not applications.count():
        request.user.message_set.create(message='No applications selected.')
        return HttpResponseRedirect(reverse('evaluation_list', kwargs={'session_id': session_id}))

    if action == 'email':
        #return HttpResponseRedirect(reverse('evaluation_emailform'))
        return evaluation_emailform(request, session_id)
    # bulk actions for state changes
    # (do i want to iterate and individually save each app, to emit post-save signals?)
    # TODO: validation check for bad state changes 
    elif action == 'state-accept':
        applications.update(status='i')
    elif action == 'state-interviewed':
        applications.update(status='p')
    elif action == 'state-hire':
        applications.update(status='a')
    elif action == 'state-reject-nomail':
        applications.update(status='u')
    elif action == 'state-reject-email':
        applications.update(status='u')
        # need to send rejection email in this case too
        emails = []
        for app in applications:
            emails.append(app.profile.user2.email)

        send_mail(subject=session.rejection_email_subject,
                  txtMessage=None,
                  htmlMessage=session.rejection_email,
                  fromemail=session.rejection_email_from,
                  recipients=emails,
                  use_template=False)
        
    request.user.message_set.create(message='Evaluations updated')
    return HttpResponseRedirect(reverse('evaluation_list', kwargs={'session_id': session_id}))

@permission_required('overseas')
def evaluation_emailform(request, session_id):
    """
    Display new email form
    """
    session = get_object_or_404(Session, id=session_id)

    if request.method == 'POST':
        app_id = []
        for field in request.POST:
            if field[0:4] == 'app-':
                try:
                    app_id.append(int(field[4:]))
                except:
                    pass
        applications = Application.objects.filter(id__in=app_id, session=session)
    
    form = EmailForm()
        
    return render_to_response("volunteering/evaluation/email_compose.html",
                              {'form': form,
                               'applications': applications, 
                               'session': session},
                              context_instance=RequestContext(request))

@permission_required('overseas')
def evaluation_emailpreview(request, session_id):
    """
    Preview email - including HTML body, and ability to edit email
    """
    session = get_object_or_404(Session, id=session_id)

    if request.method == 'POST':
        app_id = []
        for field in request.POST:
            if field[0:4] == 'app-':
                try:
                    app_id.append(int(field[4:]))
                except:
                    pass
        applications = Application.objects.filter(id__in=app_id, session=session)
    
        form = EmailForm(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data
        else:
            data = None
            
        return render_to_response("volunteering/evaluation/email_preview.html",
                                  {'form': form,
                                   'data': data,
                                   'applications': applications,
                                   'session': session},
                                   context_instance=RequestContext(request))
    else:
        return HttpResponseForbidden()
    
@permission_required('overseas')
def evaluation_emailsend(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    if request.method == 'POST':
        app_id = []
        for field in request.POST:
            if field[0:4] == 'app-':
                try:
                    app_id.append(int(field[4:]))
                except:
                    pass
        applications = Application.objects.filter(id__in=app_id, session=session)
    
        form = EmailForm(request.POST)
        
        if form.is_valid():     # should always be true..!!!
            
            sender = '"%s" <%s>' % (form.cleaned_data['sendername'],
                                    form.cleaned_data['senderemail'])
    
            emails = []
            for app in applications:
                emails.append(app.profile.user2.email)
                try:
                    eval = app.evaluation
                    eval.last_email = datetime.now()
                    eval.save()
                except:
                    pass
    
            send_mail(subject=form.cleaned_data['subject'],
                      txtMessage=None,
                      htmlMessage=form.cleaned_data['body'],
                      fromemail=sender,
                      recipients=emails,
                      use_template=False)
    
        request.user.message_set.create(message="Email sent")
        return HttpResponseRedirect(reverse('evaluation_list', kwargs={'session_id': session.id}))
    else:
        return HttpResponseForbidden()
    
