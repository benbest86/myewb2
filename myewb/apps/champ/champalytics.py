"""myEWB CHAMP analytics

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

import csv, copy
from datetime import date

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseNotFound, HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.db.models import Q
from django.template import RequestContext
from django.template.loader import render_to_string

from base_groups.decorators import group_admin_required
from networks.decorators import chapter_president_required, chapter_exec_required
from networks.models import Network
from champ.models import *
from champ.views import *
from siteutils import schoolyear
from siteutils.helpers import fix_encoding, copy_model_instance
from siteutils.http import JsonResponse

def default(request):
    if not request.GET.get('stage', None):
        return select_graph(request)
    elif request.GET['stage'] == 'options' or request.GET['stage'] == 'draw':
        stage = request.GET['stage']
        graphtype = request.GET.get('graphtype', None)

        if graphtype == 'Progress to goal':
            if stage == 'options':
                return progress_options(request)
            elif stage == 'draw':
                return progress_draw(request)
                
        elif graphtype == 'Contribution to national':
            return contribution_draw(request)
        
        elif graphtype == 'Year over year':
            return year_draw(request)
        
    return HttpResponse("Internal error - lost stage")
        
def select_graph(request):
    metric = request.GET.get('metric', '')
    group = request.GET.get('group', '')
    
    return render_to_response('champ/champalytics/select.html',
                              {'metric': metric,
                               'group': group},
                              context_instance=RequestContext(request))
                              
def build_stats(group_slug=None, year=None):
    if not year:
        year = schoolyear.school_year()
        
    activity_filters, metric_filters = build_filters(year)
    
    if group_slug:
        grp = get_object_or_404(Network, slug=group_slug)
        
        if grp.is_chapter():
            metric_filters.append({'activity__group__slug': group_slug})

    metric_filters.append({'activity__visible': True})
    metric_filters.append({'activity__confirmed': True})
    context = run_stats(metric_filters)

    natl_activity_filters, natl_metric_filters = build_filters(year)
    natl_metric_filters.append({'activity__visible': True})
    natl_metric_filters.append({'activity__confirmed': True})
    natl_context = run_stats(natl_metric_filters)

    return context, natl_context
    
def build_stats_for(group_slug=None, metric=None, year=None):
    if not year:
        year = schoolyear.school_year()
        
    activity_filters, metric_filters = build_filters(year)
    
    if group_slug:
        grp = get_object_or_404(Network, slug=group_slug)
        
        if grp.is_chapter():
            metric_filters.append({'activity__group__slug': group_slug})

    metric_filters.append({'activity__visible': True})
    metric_filters.append({'activity__confirmed': True})
    context = run_stats_for(metric_filters, metric)

    natl_activity_filters, natl_metric_filters = build_filters(year)
    natl_metric_filters.append({'activity__visible': True})
    natl_metric_filters.append({'activity__confirmed': True})
    natl_context = run_stats_for(natl_metric_filters, metric)

    return context, natl_context


def progress_options(request):
    metric = request.GET.get('metric', '')
    group = request.GET.get('group', '')
    
    return render_to_response('champ/champalytics/progress_options.html',
                              {'metric': metric,
                               'group': group,
                               'namedict': aggregates.CHAMP_AGGREGATES},
                              context_instance=RequestContext(request))
                              
def progress_draw(request):
    metric = request.GET.get('metric', '')
    group = request.GET.get('group', '')
    progressby = request.GET.get('progressby', '')
    context = {}

    natl_goals = aggregates.CHAMP_AGGREGATES
    champsays = []
    
    if progressby == 'formetric' and metric:
        allgroups = Network.objects.filter(chapter_info__isnull=False, is_active=True).order_by('name')

        progress = {}
        stats, natlstats = build_stats_for(metric=metric)
        name, ngoal = natl_goals[metric]
        useabsolute = request.GET.get('useabsolute', None)
        
        if useabsolute:
            progress['national'] = (stats, stats, ngoal)
        else:
            if ngoal:
                progress['national'] = (stats * 100 / ngoal, stats, ngoal)
            else:
                progress['national'] = (100, stats, ngoal)
        
        for g in allgroups:
            yp = YearPlan.objects.filter(group=g, year=schoolyear.school_year())
            if yp.count():
                yearplan = yp[0]
            else:
                yearplan = None
                
            if yearplan or useabsolute:
                stats, nstats = build_stats_for(g.slug, metric)

                if yearplan:                
                    yearplan_name = aggregates.YEARPLAN_MAP[metric]
                    goal = getattr(yearplan, yearplan_name)
                else:
                    goal = 0
                
                if useabsolute or goal:
                    if useabsolute:
                        progress[g.slug] = (stats, stats, goal)
                    else:
                        progress[g.slug] = (stats * 100 / goal, stats, goal)
                    
                        if g.slug == group:
                            myprogress,temp1,temp2 = progress[g.slug]
                            natlprogress,temp1,temp2 = progress['national']
                            if myprogress == 0:
                                champsays.append("Looks like you haven't done much yet; need a hand?");
                            elif myprogress - natlprogress > 20:
                                champsays.append("Way to go, you're well above national average!");
                            elif myprogress - natlprogress > 0:
                                champsays.append("You're above average here, keep it up!");
                            elif myprogress - natlprogress == 0:
                                champsays.append("You're right on national average.  What are the odds...");
                            elif myprogress - natlprogress > -20:
                                champsays.append("You're just under national average... a bit of work and you'll be on top!");
                            elif myprogress - natlprogress < -20:
                                champsays.append("Looks like this is an area for improvement; need a hand?");
                            
            # can be used to test the graph with more lines...
            #else:
            #    progress[g.slug] = 35
            
        context['progress'] = progress
        context['useabsolute'] = useabsolute
        template = 'progress_metric'
        
    
    elif progressby == 'forchapter' and group:
        yp = YearPlan.objects.filter(group__slug=group, year=schoolyear.school_year())
        if yp.count():
            yearplan = yp[0]
            stats, national = build_stats(group)
            
            chapter_progress = {}
            national_progress = {}

            for s in stats:
                yearplan_name = aggregates.YEARPLAN_MAP[s]
                goal = getattr(yearplan, yearplan_name)
                
                name, ngoal = natl_goals[s]
                if ngoal:
                    nprogress = national[s] * 100 / ngoal
                else:
                    nprogress = 0
                
                if goal:
                    progress = stats[s] * 100 / goal

                    mname, natlgoal = aggregates.CHAMP_AGGREGATES[s]
                    if progress >= 100:
                        champsays.append("You've hit your goal for %s, you champion!" % mname);
                    elif progress < 100 and progress > 80:
                        champsays.append("You've almost hit your %s goal - way to go!" % mname);
                    elif progress < 30 and progress > 10:
                        champsays.append("Your %s numbers are a bit low... need some help?" % mname);
                    elif progress < 10:
                        champsays.append("Woah, watch out for %s - better get moving..." % mname);
                    
                else:
                    progress = -1
                    
                chapter_progress[s] = (progress, stats[s], goal, nprogress, national[s], ngoal)
            
            context['chapter_progress'] = chapter_progress
            
            if request.GET.get('includenatl', None):
                context['includenatl'] = True
            
        else:
            context['noyearplan'] = True
    
        context['champsays'] = champsays
        template = 'progress_chapter'
                
    else:
        return HttpResponse('oops')
    
    context['champsays'] = champsays
    context['group'] = group
    context['metric'] = metric
    context['namedict'] = aggregates.CHAMP_AGGREGATES    
    return render_to_response('champ/champalytics/' + template + '.html',
                              context,
                              context_instance=RequestContext(request))
                              
def contribution_draw(request):
    metric = request.GET.get('metric', '')
    group = request.GET.get('group', '')
    context = {}

    champsays = []
    
    stats, natlstats = build_stats_for(group_slug=group, metric=metric)
    context['metric_chapter'] = stats
    context['metric_national'] = natlstats - stats
    if context['metric_chapter'] == 0:
        context['metric_chapter'] = 0.001
    if context['metric_national'] == 0:
        context['metric_national'] = 0.001

    mname, natlgoal = aggregates.CHAMP_AGGREGATES[metric]                    
    if stats < 5:
        champsays.append("Looks like your %s program is just getting started..." % mname)
    if natlstats - stats < 5:
        champsays.append("I can't believe it - you're carrying the organization in %s!" % mname)
    elif natlstats - stats < (stats / 2):
        champsays.append("Show 'em how it's done for %s!" % mname)
    elif natlstats - stats < stats:
        champsays.append("Woah, you're really rocking out on %s - you account for over half of all EWB's numbers!" % mname)
        
    stats, national = build_stats(group)
    contributions = {}
    for s in stats:
        if national[s]:
            contributions[s] = (stats[s] * 100 / national[s], stats[s], national[s])
            
            if national[s] - stats[s] < stats[s]:
                mname, natlgoal = aggregates.CHAMP_AGGREGATES[s]
                champsays.append("Tell me how it's done - your %s numbers are amazing!" % mname)
        else:
            contributions[s] = (0, 0, 0)

    context['contributions'] = contributions            
    context['champsays'] = champsays
    context['namedict'] = aggregates.CHAMP_AGGREGATES    
    
    return render_to_response('champ/champalytics/contribution.html',
                              context,
                              context_instance=RequestContext(request))

def year_draw(request):
    metric = request.GET.get('metric', '')
    group = request.GET.get('group', '')
    context = {}

    champsays = []
    history = []

    for y in range(2007, schoolyear.school_year() + 1):
        if group and group != "none":
            stats, natlstats = build_stats_for(metric=metric, group_slug=group, year=y)
        else:
            stats, natlstats = build_stats_for(metric=metric, year=y)
        history.append((y, stats, natlstats))

    context['history'] = history
    context['champsays'] = champsays
    context['metric'] = metric
    context['group'] = group
    context['namedict'] = aggregates.CHAMP_AGGREGATES    
    
    return render_to_response('champ/champalytics/years.html',
                              context,
                              context_instance=RequestContext(request))

