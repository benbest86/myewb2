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

from volunteering.models import Session, ApplicationQuestion, InterviewQuestion, EvaluationCriterion
from volunteering.forms import SessionForm, ApplicationQuestionForm, InterviewQuestionForm, EvaluationCriterionForm

@permission_required('overseas')
def sessions(request):
    sessions = Session.objects.all()

    return render_to_response('volunteering/session/list.html', {
        "session_list": sessions,
    }, context_instance=RequestContext(request))

@permission_required('overseas')
def session_detail(request, object_id):
    session = get_object_or_404(Session, id=object_id)
    
    return render_to_response('volunteering/session/detail.html',
                              {'session': session},
                              context_instance=RequestContext(request))

@permission_required('overseas')
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
            return HttpResponseRedirect(reverse('session_detail',
                                                kwargs={'object_id': session.id}))
        
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
                                   
@permission_required('overseas')
def session_clone(request, new_id):
    old_session = get_object_or_404(Session, id=new_id)
    
    session = Session(en_instructions=old_session.en_instructions,
                      fr_instructions=old_session.fr_instructions,
                      close_email_subject=old_session.close_email_subject,
                      close_email_from=old_session.close_email_from,
                      close_email=old_session.close_email,
                      rejection_email_subject=old_session.rejection_email_subject,
                      rejection_email_from=old_session.rejection_email_from,
                      rejection_email=old_session.rejection_email)

    if request.method == 'POST':
        form = SessionForm(request.POST, instance=session)
        
        if form.is_valid():
            session = form.save()
            
            # copy questions and criteria now too
            questions = ApplicationQuestion.objects.filter(session=old_session)
            for q in questions:
                q2 = q.clone()
                q2.pk = None
                q2.session = session
                q2.save()

            questions = InterviewQuestion.objects.filter(session=old_session)
            for q in questions:
                q2 = q.clone()
                q2.pk = None
                q2.session = session
                q2.save()
                
            criteria = EvaluationCriterion.objects.filter(session=old_session)
            for c in criteria:
                c2 = copy(c)
                c2.pk = None
                c2.session = session
                c2.save()
                
            return HttpResponseRedirect(reverse('session_detail',
                                                kwargs={'object_id': session.id}))
        
    else:
        form = SessionForm(instance=session)
        
    return render_to_response('volunteering/session/form.html',
                              {'session': None,
                               'form': form},
                               context_instance=RequestContext(request))

@permission_required('overseas')
def question_edit(request, object_id):
    question = get_object_or_404(ApplicationQuestion, id=object_id)
        
    if request.method == 'POST':
        form = ApplicationQuestionForm(request.POST, instance=question)
            
        if form.is_valid():
            form.save()
            return HttpResponse("success");
        
    else:
        form = ApplicationQuestionForm(instance=question)
    
    return render_to_response('volunteering/question/form.html',
                              {'question': question,
                               'form': form},
                               context_instance=RequestContext(request))
                                   
@permission_required('overseas')
def question_new(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    
    if request.method == 'POST':
        form = ApplicationQuestionForm(request.POST)
        
        if form.is_valid():
            question = form.save(commit=False)
            question.session = session
            
            last_question = ApplicationQuestion.objects.filter(session=session).count()
            question.question_order = last_question + 1
            
            question.save()
            return HttpResponse("success")
    else:
        form = ApplicationQuestionForm()
        
    return render_to_response('volunteering/question/form.html',
                                {'question': None,
                                 'form': form},
                                context_instance=RequestContext(request))

@permission_required('overseas')
def question_delete(request):
    if request.method == 'POST' and request.POST.get('question_id', None):
        question_id = request.POST.get('question_id', None)
        question = get_object_or_404(ApplicationQuestion, id=question_id)
        session = question.session
        order = question.question_order
        question.delete()
        
        later_questions = ApplicationQuestion.objects.filter(session=session,
                                                             question_order__gt=order)
        for q in later_questions:
            q.question_order = q.question_order - 1
            q.save()
            
        return HttpResponse("success")
            
    return HttpResponse("invalid")

@permission_required('overseas')
def question_reorder(request):
    if request.method == 'POST' and request.POST.get('question_id', None) and request.POST.get('new_order', None):
        question_id = request.POST.get('question_id', None)
        question = get_object_or_404(ApplicationQuestion, id=question_id)
        current_order = question.question_order
        new_order = request.POST.get('new_order', None)
        
        if current_order != new_order:
            later_questions = ApplicationQuestion.objects.filter(session=question.session,
                                                                 question_order__gt=current_order)
            for q in later_questions:
                q.question_order = q.question_order - 1
                q.save()
                
            later_questions = ApplicationQuestion.objects.filter(session=question.session,
                                                                 question_order__gte=new_order)
            for q in later_questions:
                q.question_order = q.question_order + 1
                q.save()
                
            question.question_order = new_order
            question.save()
            
        return HttpResponse("success")
            
    return HttpResponse("invalid")

@permission_required('overseas')
def interview_question_edit(request, object_id):
    question = get_object_or_404(InterviewQuestion, id=object_id)
        
    if request.method == 'POST':
        form = InterviewQuestionForm(request.POST, instance=question)
            
        if form.is_valid():
            form.save()
            return HttpResponse("success");
        
    else:
        form = InterviewQuestionForm(instance=question)
    
    return render_to_response('volunteering/question/form.html',
                              {'question': question,
                               'form': form},
                               context_instance=RequestContext(request))
                                   
@permission_required('overseas')
def interview_question_new(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    
    if request.method == 'POST':
        form = InterviewQuestionForm(request.POST)
        
        if form.is_valid():
            question = form.save(commit=False)
            question.session = session
            
            last_question = InterviewQuestion.objects.filter(session=session).count()
            question.question_order = last_question + 1
            
            question.save()
            return HttpResponse("success")
    else:
        form = InterviewQuestionForm()
        
    return render_to_response('volunteering/question/form.html',
                                {'question': None,
                                 'form': form},
                                context_instance=RequestContext(request))

@permission_required('overseas')
def interview_question_delete(request):
    if request.method == 'POST' and request.POST.get('question_id', None):
        question_id = request.POST.get('question_id', None)
        question = get_object_or_404(InterviewQuestion, id=question_id)
        session = question.session
        order = question.question_order
        question.delete()
        
        later_questions = InterviewQuestion.objects.filter(session=session,
                                                           question_order__gt=order)
        for q in later_questions:
            q.question_order = q.question_order - 1
            q.save()
            
        return HttpResponse("success")
            
    return HttpResponse("invalid")

@permission_required('overseas')
def interview_question_reorder(request):
    if request.method == 'POST' and request.POST.get('question_id', None) and request.POST.get('new_order', None):
        question_id = request.POST.get('question_id', None)
        question = get_object_or_404(InterviewQuestion, id=question_id)
        current_order = question.question_order
        new_order = request.POST.get('new_order', None)
        
        if current_order != new_order:
            later_questions = InterviewQuestion.objects.filter(session=question.session,
                                                               question_order__gt=current_order)
            for q in later_questions:
                q.question_order = q.question_order - 1
                q.save()
                
            later_questions = InterviewQuestion.objects.filter(session=question.session,
                                                               question_order__gte=new_order)
            for q in later_questions:
                q.question_order = q.question_order + 1
                q.save()
                
            question.question_order = new_order
            question.save()
            
        return HttpResponse("success")
            
    return HttpResponse("invalid")

# TODO: criteria and question views are almost 100% identical.
# I should spin them into my own generic views...
@permission_required('overseas')
def criteria_edit(request, object_id):
    criteria = get_object_or_404(EvaluationCriterion, id=object_id)
        
    if request.method == 'POST':
        form = EvaluationCriterionForm(request.POST, instance=criteria)
            
        if form.is_valid():
            form.save()
            return HttpResponse("success");
        
    else:
        form = EvaluationCriterionForm(instance=criteria)
    
    return render_to_response('volunteering/question/form.html',
                              {'question': criteria,
                               'form': form},
                               context_instance=RequestContext(request))
                                   
@permission_required('overseas')
def criteria_new(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    
    if request.method == 'POST':
        form = EvaluationCriterionForm(request.POST)
        
        if form.is_valid():
            criteria = form.save(commit=False)
            criteria.session = session
            
            last_criteria = EvaluationCriterion.objects.filter(session=session).count()
            criteria.criteria_order = last_criteria + 1
            
            criteria.save()
            return HttpResponse("success")
    else:
        form = EvaluationCriterionForm()
        
    return render_to_response('volunteering/question/form.html',
                                {'question': None,
                                 'form': form},
                                context_instance=RequestContext(request))

@permission_required('overseas')
def criteria_delete(request):
    if request.method == 'POST' and request.POST.get('criteria_id', None):
        criteria_id = request.POST.get('criteria_id', None)
        criteria = get_object_or_404(EvaluationCriterion, id=criteria_id)
        session = criteria.session
        order = criteria.criteria_order
        criteria.delete()
        
        later_criteria = EvaluationCriterion.objects.filter(session=session,
                                                  criteria_order__gt=order)
        for q in later_criteria:
            q.criteria_order = q.criteria_order - 1
            q.save()
            
        return HttpResponse("success")
            
    return HttpResponse("invalid")

@permission_required('overseas')
def criteria_reorder(request):
    if request.method == 'POST' and request.POST.get('criteria_id', None) and request.POST.get('new_order', None):
        criteria_id = request.POST.get('criteria_id', None)
        criteria = get_object_or_404(EvaluationCriterion, id=criteria_id)
        current_order = criteria.criteria_order
        new_order = request.POST.get('new_order', None)
        
        if current_order != new_order:
            later_criteria = EvaluationCriterion.objects.filter(session=criteria.session,
                                                      criteria_order__gt=current_order)
            for q in later_criteria:
                q.criteria_order = q.criteria_order - 1
                q.save()
                
            later_criteria = EvaluationCriterion.objects.filter(session=criteria.session,
                                                      criteria_order__gte=new_order)
            for q in later_criteria:
                q.criteria_order = q.criteria_order + 1
                q.save()
                
            criteria.criteria_order = new_order
            criteria.save()
            
        return HttpResponse("success")
            
    return HttpResponse("invalid")


