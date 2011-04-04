from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.db.models import Q
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext_lazy as _

from jobboard.forms import JobPostingForm
from jobboard.models import JobPosting, Skill, URGENCY_CHOICES, TIME_CHOICES
from siteutils.shortcuts import get_object_or_none

def add_filter(request, open_jobs, field, filters):
    if request.GET.get(field, None):
        comparison = request.GET[field]
        value = request.GET.get("%s2" % field, '')
        
        if (comparison == 'lt' or comparison == 'gt') and True:     # validate value too!
            filters[field] = (comparison, value)
            
            kwargs = {}
            if comparison == 'lt':
                kwargs["%s__lte" % field] = value
            else:
                kwargs["%s__gte" % field] = value
            open_jobs = open_jobs.filter(**kwargs)

    return open_jobs, filters
    
def list(request):
    open_jobs = JobPosting.objects.open()
    my_jobs = JobPosting.objects.accepted(request.user)
    bid_jobs = JobPosting.objects.bid(request.user)
    watching_jobs = JobPosting.objects.following(request.user)
    my_postings = JobPosting.objects.owned_by(request.user)
    closed_jobs = JobPosting.objects.closed(request.user)
    
    # work with filters
    filters = {'deadline': ('', ''),
               'urgency': ('', ''),
               'time_required': ('', ''),
               'skills': ('', {})}
    
    open_jobs, filters = add_filter(request, open_jobs, 'deadline', filters)
    open_jobs, filters = add_filter(request, open_jobs, 'urgency', filters)
    open_jobs, filters = add_filter(request, open_jobs, 'time_required', filters)

    if request.GET.get('skills', None):
        comparison = request.GET['skills']
        value = request.GET.getlist('skills2')
        
        if (comparison == 'any' or comparison == 'all' or comparison == 'none') and True:     # validate deadline2 too!
            filters['skills'] = (comparison, value)
            
            if comparison == 'any':
                open_jobs = open_jobs.filter(skills__in=value).distinct()
            elif comparison == 'all':
                for skill in value:
                    open_jobs = open_jobs.filter(skills__id=skill)
            else:
                open_jobs = open_jobs.exclude(skills__in=value)

    
    allskills = Skill.objects.all()
    filters_active = False
    for f1, f2 in filters.items():
        if f2[0]:
            filters_active = True

    # sorting
    # (is this necessary? why doesn't autosort do this for me..??)
    if request.GET.get('sort', None):
        if request.GET.get('dir', 'desc') == 'asc':
            open_jobs = open_jobs.order_by(request.GET['sort'])
        else:
            open_jobs = open_jobs.order_by('-%s' % request.GET['sort'])
            
    return render_to_response("jobboard/list.html",
                              {"my_postings": my_postings,
                               "my_jobs": my_jobs,
                               "open_jobs": open_jobs,
                               "bid_jobs": bid_jobs,
                               "watching_jobs": watching_jobs,
                               "closed_jobs": closed_jobs,
                               "URGENCY_CHOICES": URGENCY_CHOICES,
                               "TIME_CHOICES": TIME_CHOICES,
                               "allskills": allskills,
                               "filters": filters,
                               "filters_active": filters_active},
                              context_instance=RequestContext(request))

def detail(request, id):
    job = get_object_or_404(JobPosting, id=id)
    
    return render_to_response("jobboard/detail.html",
                              {"job": job},
                              context_instance=RequestContext(request))

@login_required
def edit(request, id=None):
    if id:
        job = get_object_or_404(JobPosting, id=id)
    else:
        job = None
        
    if request.method == 'POST':
        if job:
            form = JobPostingForm(request.POST, instance=job)
        else:
            form = JobPostingForm(request.POST, instance=job)
        
        if form.is_valid():
            job = form.save(commit=False)
            job.owner = request.user
            job.save()
            
            # is my django-foo dropping? why is this needed?
            job.skills = form.cleaned_data['skills']
            job.save()
                
            request.user.message_set.create(message='Posting updated!')
            return HttpResponseRedirect(reverse('jobboard_detail', kwargs={'id': job.id}))
        
    else:
        if job:
            form = JobPostingForm(instance=job)
        else:
            form = JobPostingForm()
        
    return render_to_response("jobboard/edit.html",
                              {"form": form,
                               "job": job},
                              context_instance=RequestContext(request))

@login_required
def bid(request, id):
    job = get_object_or_404(JobPosting, id=id)
    
    job.bid_users.add(request.user)
    
    request.user.message_set.create(message='You have bid for this job.')
    return HttpResponseRedirect(reverse('jobboard_detail', kwargs={'id': job.id}))

@login_required
def watch(request, id):
    job = get_object_or_404(JobPosting, id=id)
    
    job.following_users.add(request.user)
    
    request.user.message_set.create(message='You are now watching this job.')
    return HttpResponseRedirect(reverse('jobboard_detail', kwargs={'id': job.id}))

@login_required
def bid_cancel(request, id):
    job = get_object_or_404(JobPosting, id=id)
    
    job.bid_users.remove(request.user)
    
    request.user.message_set.create(message='You have cancelled your bid.')
    return HttpResponseRedirect(reverse('jobboard_detail', kwargs={'id': job.id}))

@login_required
def watch_cancel(request, id):
    job = get_object_or_404(JobPosting, id=id)
    
    job.following_users.remove(request.user)
    
    request.user.message_set.create(message='You are now longer watching this job.')
    return HttpResponseRedirect(reverse('jobboard_detail', kwargs={'id': job.id}))

@login_required
def close(request, id):
    if request.user.has_module_perms('jobboard'):
        job = get_object_or_404(JobPosting, id=id)    
    else:
        job = get_object_or_404(JobPosting, id=id, owner=request.user)
        
    job.active=False
    job.save()
    
    request.user.message_set.create(message='Job closed.')
    return HttpResponseRedirect(reverse('jobboard_detail', kwargs={'id': job.id}))


@login_required
def open(request, id):
    if request.user.has_module_perms('jobboard'):
        job = get_object_or_404(JobPosting, id=id)    
    else:
        job = get_object_or_404(JobPosting, id=id, owner=request.user)
        
    job.active=True
    job.save()
    
    request.user.message_set.create(message='Job re-opened.')
    return HttpResponseRedirect(reverse('jobboard_detail', kwargs={'id': job.id}))

@login_required
def accept(request, id, username):
    job = get_object_or_404(JobPosting, id=id, owner=request.user)
    user = get_object_or_404(User, username=username)
    
    job.bid_users.remove(user)
    job.accepted_users.add(user)
    
    request.user.message_set.create(message="You have accepted %s for the job." % user.visible_name())
    return HttpResponseRedirect(reverse('jobboard_detail', kwargs={'id': job.id}))
    
@login_required
def accept_cancel(request, id, username):
    job = get_object_or_404(JobPosting, id=id, owner=request.user)
    user = get_object_or_404(User, username=username)
    
    job.accepted_users.remove(user)
    job.bid_users.add(user)
    
    request.user.message_set.create(message="You have removed %s from the job." % user.visible_name())
    return HttpResponseRedirect(reverse('jobboard_detail', kwargs={'id': job.id}))
