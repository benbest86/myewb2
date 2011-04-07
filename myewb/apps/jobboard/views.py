from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.db.models import Q
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext_lazy as _
from urllib import quote_plus

from jobboard.forms import JobPostingForm
from jobboard.models import JobPosting, Skill, URGENCY_CHOICES, TIME_CHOICES, JobFilter, JobInterest, Location
from siteutils.shortcuts import get_object_or_none
from siteutils.http import JsonResponse

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
    if request.user.is_authenticated():
        saved_filters = JobFilter.objects.filter(user=request.user)
    else:
        saved_filters = []
    
    # work with filters
    filters = {'deadline': ('', ''),
               'urgency': ('', ''),
               'time_required': ('', ''),
               'skills': ('', {}),
               'location': ('', {}),
               'search': ('', '')}
    
    open_jobs, filters = add_filter(request, open_jobs, 'deadline', filters)
    open_jobs, filters = add_filter(request, open_jobs, 'urgency', filters)
    open_jobs, filters = add_filter(request, open_jobs, 'time_required', filters)

    if request.GET.get('skills', None):
        comparison = request.GET['skills']
        value = request.GET.getlist('skills2')
        
        if (comparison == 'any' or comparison == 'all' or comparison == 'none'):     # validate deadline2 too!
            filters['skills'] = (comparison, value)
            
            if comparison == 'any':
                open_jobs = open_jobs.filter(skills__in=value).distinct()
            elif comparison == 'all':
                for skill in value:
                    open_jobs = open_jobs.filter(skills__id=skill)
            else:
                open_jobs = open_jobs.exclude(skills__in=value)

    if request.GET.get('location', None):
        comparison = request.GET['location']
        value = request.GET.getlist('location2')
        
        if comparison == 'oneof':     # validate deadline2 too!
            filters['location'] = (comparison, value)
            open_jobs = open_jobs.filter(location__in=value).distinct()

    if request.GET.get('search', None):
        value = request.GET['search']
        filters['search'] = (value, '')
        open_jobs = open_jobs.filter(Q(description__icontains=value) | Q(name__icontains=value))
        
    if request.GET.get('skills', None) or request.GET.get('location', None) or request.GET.get('search', None): 
        open_jobs = open_jobs.distinct()

    allskills = Skill.objects.all()
    alllocations = Location.objects.all()
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
                               "alllocations": alllocations,
                               "filters": filters,
                               "filters_active": filters_active,
                               "saved_filters": saved_filters},
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
            help = """When writing a description for your project/task consider the 5 main dimensions people consider when picking up an opportunity in EWB:

    * National vs local
    * Strategy (more entrepreneurial) vs support (more execution)
    * Constrained vs open-ended
    * Team (shared) responsibility vs solo responsibility
    * Programmatic (GE,YE) vs skill focused (coaching, editing, programming)
 
And remember top EWBers love 3 main things: impact, challenges and working with other EWBers. """
            form = JobPostingForm(initial={'description': help})
        
    return render_to_response("jobboard/edit.html",
                              {"form": form,
                               "job": job},
                              context_instance=RequestContext(request))

@login_required
def bid(request, id):
    job = get_object_or_404(JobPosting, id=id)
    
    bid, created = JobInterest.objects.get_or_create(user=request.user, job=job)
    
    if request.POST.get('statement', None):
        bid.statement = request.POST['statement']
        bid.save()
    
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
    
    bids = JobInterest.objects.filter(user=request.user, job=job)
    for b in bids:
        b.delete()
    
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
    
    bids = JobInterest.objects.filter(user=user, job=job)
    for b in bids:
        b.accepted=True
        b.save()

    request.user.message_set.create(message="You have accepted %s for the job." % user.visible_name())
    return HttpResponseRedirect(reverse('jobboard_detail', kwargs={'id': job.id}))
    
@login_required
def accept_cancel(request, id, username):
    job = get_object_or_404(JobPosting, id=id, owner=request.user)
    user = get_object_or_404(User, username=username)
    
    bids = JobInterest.objects.filter(user=user, job=job)
    for b in bids:
        b.accepted=False
        b.save()

    request.user.message_set.create(message="You have removed %s from the job." % user.visible_name())
    return HttpResponseRedirect(reverse('jobboard_detail', kwargs={'id': job.id}))

@login_required
def statement(request, id, username):
    job = get_object_or_404(JobPosting, id=id, owner=request.user)
    user = get_object_or_404(User, username=username)
    
    bids = JobInterest.objects.filter(user=user, job=job)
    bid = bids[0]

    return HttpResponse(bid.statement)
    
@login_required
def filters_save(request):
    if request.method == 'POST':
        kwargs = {}
        kwargs['user'] = request.user
        
        if request.POST.get('deadline', None) and request.POST.get('deadline2', None):
            kwargs['deadline_comparison'] = request.POST['deadline']
            kwargs['deadline'] = request.POST['deadline2']
        
        if request.POST.get('urgency', None) and request.POST.get('urgency2', None):
            kwargs['urgency_comparison'] = request.POST['urgency']
            kwargs['urgency'] = request.POST['urgency2']
        
        if request.POST.get('skills', None) and request.POST.get('skills2', None):
            kwargs['skills_comparison'] = request.POST['skills']
            
        if request.POST.get('location', None) and request.POST.get('location2', None):
            kwargs['location_comparison'] = request.POST['location']
            
        if request.POST.get('time_required', None) and request.POST.get('time_required2', None):
            kwargs['time_required_comparison'] = request.POST['time_required']
            kwargs['time_required'] = request.POST['time_required2']
            
        if request.POST.get('search', None):
            kwargs['search'] = request.POST['search']
            
        filter = JobFilter.objects.filter(**kwargs)
        
        skills = []
        for s in request.POST.getlist('skills2'):
            skill = get_object_or_none(Skill, id=s)
            if skill:
                skills.append(skill)
                filter = filter.filter(skills=skill)

        if request.POST.get('skills', None) and request.POST.get('skills2', None):
            filter = filter.exclude(~Q(skills__in=skills))
            
        locations = []
        for l in request.POST.getlist('location2'):
            location = get_object_or_none(Location, id=l)
            if location:
                locations.append(location)
                filter = filter.filter(location=location)

        if request.POST.get('location', None) and request.POST.get('location2', None):
            filter = filter.exclude(~Q(location__in=locations))
            
        if filter.count():
            filter = filter[0]
        else:
            filter = JobFilter.objects.create(**kwargs)
            for s in skills:
                filter.skills.add(s)
            for l in locations:
                filter.location.add(l)

        filter.name = request.POST.get('name', '')
        if request.POST.get('email', None):
            filter.email = True
        else:
            filter.email = False
        
        filter.save()
        
        return HttpResponse("success")
    
    else:
        return render_to_response("jobboard/filters_save.html",
                                  {},
                                  context_instance=RequestContext(request))

@login_required
def filters_load(request, id):
    filter = get_object_or_404(JobFilter, user=request.user, id=id)
    
    url = reverse('jobboard_list') + '?'

    if filter.deadline_comparison:
        url = url + "deadline=%s&deadline2=%s&" % (filter.deadline_comparison, filter.deadline)
    if filter.urgency_comparison:
        url = url + "urgency=%s&urgency2=%s&" % (filter.urgency_comparison, filter.urgency)
    if filter.time_required_comparison:
        url = url + "time_required=%s&time_required2=%s&" % (filter.time_required_comparison, filter.time_required)
    
    if filter.skills_comparison:
        url = url + "skills=%s&" % filter.skills_comparison
        for s in filter.skills.all():
            url = url + "skills2=%d&" % s.id 

    if filter.location_comparison:
        url = url + "location=%s&" % filter.location_comparison
        for l in filter.location.all():
            url = url + "location2=%d&" % l.id 

    if filter.search:
        url = url + "search=%s&" % quote_plus(filter.search)

    url = url.rstrip('&')
    
    return HttpResponseRedirect(url)

@login_required
def filters_delete(request, id):
    filter = get_object_or_404(JobFilter, user=request.user, id=id)

    filter.delete()
    return HttpResponse("success")