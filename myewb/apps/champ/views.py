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
from django.http import HttpResponseNotFound, HttpResponseRedirect, HttpResponse
from django.db.models import Q
from django.template import RequestContext

from networks.models import Network
from champ.models import *

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
    
    wo_metrics = run_query(PublicAdvocacyMetrics.objects.all(), filters)
    wo_professionals = 0
    wo_presentations = 0
    for w in wo_metrics:
        wo_professionals += w.attendance 
        wo_presentations += w.presentations
    
    so_metrics = run_query(PublicAdvocacyMetrics.objects.all(), filters)
    so_students = 0
    so_presentations = 0
    for s in so_metrics:
        so_students += s.students
        so_presentations += s.presentations
    
    fundraising_metrics = run_query(PublicAdvocacyMetrics.objects.all(), filters)
    fundraising_dollars = 0
    for f in fundraising_metrics:
        fundraising_dollars += f.revenue
    
    publicity_metrics = run_query(PublicAdvocacyMetrics.objects.all(), filters)
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
    
    return render_to_response('champ/dashboard.html',
                              context,
                              context_instance=RequestContext(request))

