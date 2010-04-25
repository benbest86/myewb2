"""myEWB CHAMP views

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung

Ideally, I'd like to split out the different metric types and make them pluggable:
define a different template segment for each, then build a list and include/parse dynamically
(instead of having them fixed in run_stats() here)....
"""

from datetime import date

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseNotFound, HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.db.models import Q
from django.template import RequestContext

from base_groups.decorators import group_admin_required
from networks.models import Network
from champ.models import *
from champ.forms import *

def run_query(query, filters):
    for f in filters:
        query = query.filter(**f)
    return query

def run_stats(filters):
    # FIXME: these all need to be rewritten with aggregate functions when we go to django 1.1 !!!!!
    ml_metrics = run_query(MemberLearningMetrics.objects.all(), filters)
    ml_hours = 0
    ml_attendance = 0
    for m in ml_metrics:
        ml_hours += m.duration * m.attendance
        ml_attendance += m.attendance
        
    pe_metrics = run_query(PublicEngagementMetrics.objects.all(), filters)
    pe_people = 0
    for p in pe_metrics:
        pe_people += p.level1 + p.level2 + p.level3
    
    po_metrics = run_query(PublicAdvocacyMetrics.objects.all(), filters)
    po_contacts = 0
    for p in po_metrics:
        po_contacts += p.units
    
    ce_metrics = run_query(CurriculumEnhancementMetrics.objects.all(), filters)
    ce_students = 0
    ce_hours = 0
    for c in ce_metrics:
        ce_students += c.students
        ce_hours += c.hours
    
    wo_metrics = run_query(WorkplaceOutreachMetrics.objects.all(), filters)
    wo_professionals = 0
    wo_presentations = 0
    for w in wo_metrics:
        wo_professionals += w.attendance 
        wo_presentations += w.presentations
    
    so_metrics = run_query(SchoolOutreachMetrics.objects.all(), filters)
    so_students = 0
    so_presentations = 0
    for s in so_metrics:
        so_students += s.students
        so_presentations += s.presentations
    
    fundraising_metrics = run_query(FundraisingMetrics.objects.all(), filters)
    fundraising_dollars = 0
    for f in fundraising_metrics:
        fundraising_dollars += f.revenue
    
    publicity_metrics = run_query(PublicationMetrics.objects.all(), filters)
    publicity_hits = publicity_metrics.count()
    
    context = {}
    context['ml_hours'] = ml_hours
    context['ml_attendance'] = ml_attendance
    context['po_contacts'] = po_contacts
    context['ce_students'] = ce_students
    context['ce_hours'] = ce_hours
    context['wo_professionals'] = wo_professionals
    context['wo_presentations'] = wo_presentations
    context['so_students'] = so_students
    context['so_presentations'] = so_presentations
    context['fundraising_dollars'] = fundraising_dollars
    context['publicity_hits'] = publicity_hits
    
    return context

def build_filters(year=None, month=None, term=None):
    activity_filters = []
    metric_filters = []
    
    if year:
        activity_filters.append({'date__year': year})
        metric_filters.append({'activity__date__year': year})
    if month:
        activity_filters.append({'date__month': year})
        metric_filters.append({'activity__date__month': year})
    if year and term:
        if term == 'winter':
            start = date(year, 1, 1)
            end = date(year, 4, 31)
            activity_filters.append({'date__range': (start, end)})
            metric_filters.append({'activity__date__range': (start, end)})
        elif term == 'summer':
            start = date(year, 5, 1)
            end = date(year, 8, 31)
            activity_filters.append({'date__range': (start, end)})
            metric_filters.append({'activity__date__range': (start, end)})
        elif term == 'fall':
            start = date(year, 9, 1)
            end = date(year, 12, 31)
            activity_filters.append({'date__range': (start, end)})
            metric_filters.append({'activity__date__range': (start, end)})
            
    return activity_filters, metric_filters
    
@login_required()
def dashboard(request, year=None, month=None, term=None,
                       group_slug=None):
    activity_filters, metric_filters = build_filters(year, month, term)
    
    if group_slug:
        activity_filters.append({'group__slug': group_slug})
        metric_filters.append({'activity__group__slug': group_slug})
        
        grp = get_object_or_404(Network, slug=group_slug)
    else:
        grp = None

    metric_filters.append({'activity__confirmed': True})
    context = run_stats(metric_filters)

    context['journals'] = 0
    context['unconfirmed'] = run_query(Activity.objects.filter(confirmed=False), activity_filters).count()
    context['confirmed'] = run_query(Activity.objects.filter(confirmed=True), activity_filters).count()

    context['group'] = None    
    context['is_group_admin'] = False
    if grp:
        context['group'] = grp
    
        if grp.user_is_admin(request.user):
            context['is_group_admin'] = True
            
    context['year'] = year
    context['month'] = month
    context['term'] = term
    
    context['nowyear'] = 2010
    context['nowmonth'] = '04'
    context['nowterm'] = 'Winter'
    
    context['allgroups'] = Network.objects.filter(chapter_info__isnull=False).order_by('name')
    
    return render_to_response('champ/dashboard.html',
                              context,
                              context_instance=RequestContext(request))

@group_admin_required()
def new_activity(request, group_slug):
    group = get_object_or_404(Network, slug=group_slug)
    metric_forms = {}
    showfields = {}
    
    if request.method == 'POST':
        champ_form = ChampForm(request.POST)
        
        # also create forms for the selected metrics
        forms_valid = champ_form.is_valid()
        for m in ALLMETRICS:
            if m in request.POST:
                if m == 'all':
                    metric_forms[m] = METRICFORMS[m](request.POST)
                else:
                    metric_forms[m] = METRICFORMS[m](request.POST,
                                                     prefix=m)
                forms_valid = forms_valid and metric_forms[m].is_valid()
                showfields[m] = True

        if forms_valid:
            # save the activity
            activity = champ_form.save(commit=False)
            activity.creator = request.user
            activity.editor = request.user
            activity.group = group
            activity.save()
            
            # and save all associated metrics
            for m in metric_forms:
                if not m == 'all':
                    metric = metric_forms[m].save(commit=False)
                    metric.activity=activity
                    metric.save()
            
            request.user.message_set.create(message="Activity recorded")
            return HttpResponseRedirect(reverse('champ_dashboard', kwargs={'group_slug': group_slug}))
            
        else:
            # create all the other metric forms as blank forms
            for m in ALLMETRICS:
                if m not in metric_forms:
                    metric_forms[m] = METRICFORMS[m](prefix=m)
                    showfields[m] = False
                 
    else:
        champ_form = ChampForm()
        for m in ALLMETRICS:
            if m == 'all':
                metric_forms[m] = METRICFORMS[m]()
            else:
                metric_forms[m] = METRICFORMS[m](prefix=m)
                       
    return render_to_response('champ/new_activity.html',
                              {'group': group,
                               'champ_form': champ_form,
                               'metric_names': ALLMETRICS,
                               'metric_forms': metric_forms,
                               'showfields': showfields},
                              context_instance=RequestContext(request))
    
@group_admin_required()
def confirmed(request, group_slug):
    group = get_object_or_404(Network, slug=group_slug)
    activities = Activity.objects.filter(confirmed=True,
                                         group__slug=group_slug)
    activites = activities.order_by('-date')
    
    return render_to_response('champ/activity_list.html',
                              {'confirmed': True,
                               'activities': activities,
                               'group': group},
                               context_instance=RequestContext(request))
    
@group_admin_required()
def unconfirmed(request, group_slug):
    group = get_object_or_404(Network, slug=group_slug)
    activities = Activity.objects.filter(confirmed=False,
                                         group__slug=group_slug)
    activites = activities.order_by('-date')
    
    return render_to_response('champ/activity_list.html',
                              {'confirmed': False,
                               'activities': activities,
                               'group': group},
                               context_instance=RequestContext(request))
    
@group_admin_required()
def activity_detail(request, group_slug, activity_id):
    group = get_object_or_404(Network, slug=group_slug)
    activity = get_object_or_404(Activity, pk=activity_id)
    
    # do we want this?
    # and why do we need to use pk's? (check always fails otherwise)
    if not activity.group.pk == group.pk:
        return HttpResponseForbidden()
    
    return render_to_response('champ/activity_detail.html',
                              {'activity': activity,
                               'group': group,
                               'metric_names': ALLMETRICS},
                               context_instance=RequestContext(request))
    
@group_admin_required()
def activity_edit(request, group_slug, activity_id):
    group = get_object_or_404(Network, slug=group_slug)
    activity = get_object_or_404(Activity, pk=activity_id)
    
    if not activity.group.pk == group.pk:
        return HttpResponseForbidden()
    
    if activity.confirmed:
        request.user.message_set.create(message="This activity is already confirmed - you can't edit it any more")
        return HttpResponseRedirect(reverse('champ_activity', kwargs={'group_slug': group_slug, 'activity_id': activity_id}))

    metric_forms = {}
    showfields = {}
    
    if request.method == 'POST':
        champ_form = ChampForm(request.POST, instance=activity)
        
        # also create forms for the selected metrics.
        # initialize all to empty
        forms_valid = champ_form.is_valid()
        # then populate the ones we're using for this activity
        metrics = activity.get_metrics()
        for m in metrics:
            if m.metricname in request.POST:
                metric_forms[m.metricname] = METRICFORMS[m.metricname](request.POST,
                                                                       instance=m,
                                                                       prefix=m.metricname)
                showfields[m.metricname] = True
                forms_valid = forms_valid and metric_forms[m.metricname].is_valid()

        for m in ALLMETRICS:
            if m in request.POST and m not in metric_forms:
                if m == 'all':
                    metric_forms[m] = METRICFORMS[m](request.POST,
                                                     instance=activity)
                else:
                    metric_forms[m] = METRICFORMS[m](request.POST,
                                                     prefix=m)
                forms_valid = forms_valid and metric_forms[m].is_valid()
                showfields[m] = True
            elif m not in metric_forms:
                metric_forms[m] = METRICFORMS[m](prefix=m)
                showfields[m] = False
                
        if forms_valid:
            activity.save()
            saved_fields = {}
            for m in metrics:
                if m.metricname in request.POST:
                    metric_forms[m.metricname].save()
                    saved_fields[m.metricname] = True
                else:
                    m.delete()
            for m in ALLMETRICS:
                if m in request.POST and m not in saved_fields:
                    metric = metric_forms[m].save(commit=False)
                    metric.activity = activity
                    metric.save()
            
            request.user.message_set.create(message="Activity updated.")
            return HttpResponseRedirect(reverse('champ_activity', kwargs={'group_slug': group_slug, 'activity_id': activity_id}))
        
    else:
        champ_form = ChampForm(instance=activity)
        
        # also create forms for the selected metrics.
        # pre-populate the ones we're using for this activity
        metrics = activity.get_metrics()
        for m in metrics:
            metric_forms[m.metricname] = METRICFORMS[m.metricname](instance=m,
                                                                   prefix=m.metricname)
            showfields[m.metricname] = True
            
        # then create forms for the rest too
        for m in ALLMETRICS:
            if m not in metric_forms:
                if m == 'all': 
                    metric_forms[m] = METRICFORMS[m](instance=activity)
                else:
                    metric_forms[m] = METRICFORMS[m](prefix=m)
                showfields[m] = False

    return render_to_response('champ/new_activity.html',
                              {'group': group,
                               'champ_form': champ_form,
                               'metric_names': ALLMETRICS,
                               'metric_forms': metric_forms,
                               'showfields': showfields},
                              context_instance=RequestContext(request))

@group_admin_required()
def activity_confirm(request, group_slug, activity_id):
    group = get_object_or_404(Network, slug=group_slug)
    activity = get_object_or_404(Activity, pk=activity_id)
    
    if not activity.group.pk == group.pk:
        return HttpResponseForbidden()
    
    if activity.confirmed:
        request.user.message_set.create(message="This activity is already confirmed")

    elif not activity.can_be_confirmed():
        request.user.message_set.create(message="This activity cannot be confirmed yet")

    else:
        activity.confirmed = True
        activity.save()
        request.user.message_set.create(message="Activity confirmed.  Thanks - you rock!")
        
    return HttpResponseRedirect(reverse('champ_activity', kwargs={'group_slug': group_slug, 'activity_id': activity_id}))
