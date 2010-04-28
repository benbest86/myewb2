"""myEWB advanced profile queries

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

import cPickle as pickle

from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, loader, Template
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from base_groups.models import BaseGroup
from profiles.models import MemberProfile
from profile_query.models import Query
from profile_query.forms.query import ProfileQueryForm, GroupQueryForm, QueryNameForm
from profile_query.types import *

@permission_required('profiles')
def list(request):
    my_queries = Query.objects.filter(owner=request.user)
    shared_queries = Query.objects.filter(shared=True).exclude(owner=request.user)
    
    return render_to_response(
            'profile_query/query_list.html', 
            {'my_queries': my_queries,
             'shared_queries': shared_queries 
            }, 
            context_instance=RequestContext(request))

@permission_required('profiles')
def save(request):
    # load up the current query, which is saved in the session
    terms = request.session.get("profilequery")
    
    if request.method == 'POST':
        form = QueryNameForm(request.POST)
        
        if form.is_valid():
            query = form.save(commit=False)
            query.terms = pickle.dumps(terms) 
            query.owner = request.user
            query.save()

            request.user.message_set.create(message="Saved")
            return HttpResponseRedirect(reverse('profile_query'))
    else:
        form = QueryNameForm()
        parsed_terms = []
        for id, term in enumerate(terms):
            # parse to human-readable format
            parsed_terms.append(parse_profile_term(term, id))
        
    return render_to_response('profile_query/query_save.html',
                              {'form': form,
                               'terms': parsed_terms},
                              context_instance=RequestContext(request))
    
@permission_required('profiles')
def load(request, id):
    query = get_object_or_404(Query, pk=id)
    
    terms = pickle.loads(str(query.terms))        # is this forced unicode-to-ascii going to bite me later?
    request.session['profilequery'] = terms
    
    request.user.message_set.create(message="Loaded")
    return HttpResponseRedirect(reverse("profile_new_query"))

@permission_required('profiles')
def new_query(request):
    profileform = None
    groupform = None
    results = None
    
    # load up the current query, which is saved in the session
    terms = request.session.get("profilequery")
    parsed_terms = []
    if terms:
        for id, term in enumerate(terms):
            # parse to human-readable format
            parsed_terms.append(parse_profile_term(term, id))
    
    # POST means we're running the query
    if request.method == 'POST' and terms:
        results = build_profile_query(terms)
    else:
        profileform = ProfileQueryForm()
        groupform = GroupQueryForm()

    return render_to_response(
            'profile_query/query.html', 
            { 
                'profileform': profileform,
                'groupform': groupform,
                'results': results,
                'terms': parsed_terms
            }, 
            context_instance=RequestContext(request))

# should templatize this instead, maybe?
def parse_profile_term(data, id=None):
    """
    Build human-readable format for a query term
    """
    terms = data.split("|")
    
    if terms[0] == 'group':
        operator, group = terms[1:]
        
        try:
            operator = GROUP_CHOICES2[operator]
            group = BaseGroup.objects.get(slug=group)
        except:
            pass
        
        return render_to_string("profile_query/groupterm.html",
                                {'operator': operator,
                                 'group': group,
                                 'results': 0,  #maybe one day
                                 'id': id})
    else:
        attribute, comparison, value = terms[1:]
        
        try:            # shouldn't happen, except when I change names during development...
            attribute = PROFILE_CHOICES[attribute]
            comparison = STRING_COMPARISONS[comparison]
        except:
            pass
        
        return render_to_string("profile_query/profileterm.html",
                                {'attribute': attribute,
                                 'comparison': comparison,
                                 'value': value,
                                 'results': 0,    # not used yet. maybe one day.
                                 'id': id})

def build_profile_query(terms):
    """
    Build a query based on submitted profile terms
    """
    results = MemberProfile.objects.all()
    
    for t in terms:
        type, attribute, comparison, value = t.split("|")
    
        # build the query filter dynamically...
        kwargs = {}
        if type == 'profile':
            kwargs[str("%s__%s" % (attribute, comparison))] = value
            
        results = results.filter(**kwargs)
    return results

@permission_required('profiles')
def addprofile(request):
    """
    Add a profile-based query term.  Is an AJAX call.
    """
    # only valid as a POST...
    if request.method == 'POST':
        f = ProfileQueryForm(request.POST)
        
        if f.is_valid():
            # get the latest term
            data = f.cleaned_data['queryfields']
            
            # retrieve the old terms, and add  to the list
            terms = request.session.get("profilequery")
            if terms == None:
                terms = []
            id = len(terms)
            terms.append(data)
            request.session['profilequery'] = terms
        
            # AJAX return is the human-readable version
            return HttpResponse(parse_profile_term(data, id))
    return Http404
    
@permission_required('profiles')
def delprofile(request, id):
    """
    Remove a profile-based query term.  Should be (but isn't currently) an AJAX call.
    """
    terms = request.session.get("profilequery")
    del terms[int(id)]
    request.session['profilequery'] = terms
    return HttpResponseRedirect(reverse('profile_new_query'))
    
@permission_required('profiles')
def addgroup(request):
    """
    Add a group-based query term.  Is an AJAX call.
    """
    # only valid as a POST...
    if request.method == 'POST':
        f = GroupQueryForm(request.POST)
        
        if f.is_valid():
            # get the latest term
            data = f.cleaned_data['queryfields']
            
            # retrieve the old terms, and add  to the list
            terms = request.session.get("profilequery")
            if terms == None:
                terms = []
            id = len(terms)
            terms.append(data)
            request.session['profilequery'] = terms
        
            # AJAX return is the human-readable version
            return HttpResponse(parse_profile_term(data, id))
    return Http404
    
@permission_required('profiles')
def delgroup(request, id):
    """
    Remove a group-based query term.  Should be (but isn't currently) an AJAX call.
    """
    terms = request.session.get("profilequery")
    del terms[int(id)]
    request.session['profilequery'] = terms
    return HttpResponseRedirect(reverse('profile_new_query'))
