"""myEWB APS applications

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author: Francis Kung
"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext_lazy as _

from volunteering.models import Session, Application, ApplicationQuestion, Answer
from volunteering.forms import SessionForm, ApplicationForm

from datetime import datetime

@login_required
def applications(request):
    # do session handling (could also do this on a cron, but eh)
    open_sessions = Session.objects.filter(active=False,
                                            open_date__lt=datetime.now(),
                                            close_date__gt=datetime.now())
    for c in open_sessions:
        c.open()
        
    close_sessions = Session.objects.filter(active=True,
                                            close_date__lt=datetime.now())
    for c in close_sessions:
        c.close()
    
    # find application lists
    applications = Application.objects.filter(profile=request.user.get_profile())
    past_applications = applications.filter(session__active=False)
    current_applications = applications.filter(session__active=True)   # FIXME: not quite
                                                   
    open_sessions = Session.objects.filter(active=True)
    sessions = []
    for s in open_sessions:
        for a in current_applications:
            if a.session == s:
                s.application = a
        sessions.append(s)
    
    return render_to_response('volunteering/application/list.html', 
                              {"past": past_applications,
                               "current": current_applications,
                               "sessions": sessions
                              },
                              context_instance=RequestContext(request))

@login_required
def application_new(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    
    # session no longer valid?
    if not session.active:
        request.user.message_set.create(message='That session is closed.')
        return HttpResponseRedirect(reverse('applications'))

    # create application        
    app, created = Application.objects.get_or_create(session=session, profile=request.user.get_profile())
    return HttpResponseRedirect(reverse('applications_edit', kwargs={'app_id': app.id}))

@login_required
def application_edit(request, app_id):
    application = get_object_or_404(Application, id=app_id, profile=request.user.get_profile())
    
    # application no longer valid?
    if not application.session.active:
        request.user.message_set.create(message='The application session has ended; you cannot edit your application any more.')
        return HttpResponseRedirect(reverse('applications_detail', kwargs={'app_id': application.id}))

    form = ApplicationForm(instance=application)
    
    # render response.  (no processing done here; that's all elsewhere in AJAX)
    return render_to_response('volunteering/application/apply.html', 
                              {"application": application,
                               "form": form,
                              },
                              context_instance=RequestContext(request))

@login_required
def application_reopen(request, app_id):
    application = get_object_or_404(Application, id=app_id, profile=request.user.get_profile())
    
    # application no longer valid?
    if not application.session.active:
        request.user.message_set.create(message='The application session has ended; you cannot edit your application any more.')
        return HttpResponseRedirect(reverse('applications_detail', kwargs={'app_id': application.id}))

    if application.complete:
        application.complete = False
        application.save()
        request.user.message_set.create(message="Your application has been re-opened.<br/>You must re-submit it for your application to be considered (even if you don't make any changes).")

    return HttpResponseRedirect(reverse('applications_edit', kwargs={'app_id': application.id}))

@login_required
def application_detail(request, app_id):
    application = get_object_or_404(Application, id=app_id, profile=request.user.get_profile())
    
    # render response.  (no processing done here; that's all elsewhere in AJAX)
    return render_to_response('volunteering/application/detail.html', 
                              {"application": application,
                              },
                              context_instance=RequestContext(request))

@login_required
def application_save(request, app_id):
    application = get_object_or_404(Application, id=app_id, profile=request.user.get_profile())
    
    # application no longer valid?
    if not application.session.active:
        request.user.message_set.create(message='The application session has ended; you cannot edit your application any more.')
        return HttpResponseRedirect(reverse('applications'))

    if request.method == 'POST' and request.is_ajax():
        form = ApplicationForm(request.POST, instance=application)
        
        if form.is_valid():
            app = form.save()
            return HttpResponse("success")
            
        return render_to_response('volunteering/application/form.html',
                                  {'application': application,
                                   'form': form
                                  },
                                  context_instance=RequestContext(request))
    
    return HttpResponseForbidden()

@login_required
def application_answer(request):
    question_id = request.POST.get('question', None)
    application_id = request.POST.get('application', None)
    
    if not question_id or not application_id:
        return HttpResponseNotFound()
    
    application = get_object_or_404(Application, id=application_id,
                                                 profile=request.user.get_profile(),
                                                 session__active=True)
    question = get_object_or_404(ApplicationQuestion, id=question_id, session=application.session)
    answer, created = Answer.objects.get_or_create(application=application, question=question)
    answer.answer = request.POST.get('answer', '')
    answer.save()
    
    return HttpResponse("saved");
    
@login_required
def application_submit(request, app_id):
    application = get_object_or_404(Application, id=app_id)
    
    application_errors = []
    if not application.en_writing or not application.en_reading or not application.en_speaking:
        application_errors.append('Please complete your English language evaluation.')
    if not application.fr_writing or not application.fr_reading or not application.fr_speaking:
        application_errors.append('Please complete your French language evaluation.')
    if not application.schooling:
        application_errors.append('Please complete your schooling information.')
    if not application.resume_text:
        application_errors.append('Please include your resume.')
    if not application.references:
        application_errors.append('Please include some references.')
    if not application.gpa:
        application_errors.append('Please enter your GPA.')
        
    for q in application.session.application_questions():
        a = Answer.objects.filter(application=application, question=q)
        if a.count() and a[0].answer:
            pass
        else:
            application_errors.append('Please complete every question.')

    if len(application_errors):
        errors = ""
        for e in application_errors:
            errors = errors + e + "<br/>"
        return HttpResponse(errors)
    else:
        request.user.message_set.create(message='Application submitted')
        application.complete = True
        application.status = 's'
        application.save()
        return HttpResponse("success")
