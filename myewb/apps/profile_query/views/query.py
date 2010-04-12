from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, loader, Template
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from profiles.models import MemberProfile
from profile_query.forms import *

@permission_required('profiles')
def profilequery(request):
    form = None
    results = None
    
    # load up the current query, which is saved in the session
    terms = request.session.get("profilequery")
    parsed_terms = []
    for id, term in enumerate(terms):
        # parse to human-readable format
        parsed_terms.append(parse_profile_term(term, id))
    
    # POST means we're running the query
    if request.method == 'POST':
        results = MemberProfile.objects.all()
        
        for t in terms:
            attribute, comparison, value = t.split("|")
        
            # build the query filter dynamically...
            kwargs = {}
            kwargs[str("%s__%s" % (attribute, comparison))] = value
            results = results.filter(**kwargs)
    else:
        form = ProfileQueryForm()

    return render_to_response(
            'profile_query/query.html', 
            { 
                'form': form,
                'results': results,
                'terms': parsed_terms
            }, 
            context_instance=RequestContext(request))

# should templatize this instead, maybe?
def parse_profile_term(data, id=None):
    """
    Build human-readable format for a query term
    """
    attribute, comparison, value = data.split("|")
    try:            # shouldn't happen, except when I change names during development...
        attribute = FIELD2[attribute]
        comparison = FIELD3[comparison]
    except:
        pass
    return render_to_string("profile_query/profileterm.html", {'attribute': attribute,
                                                               'comparison': comparison,
                                                               'value': value,
                                                               'results': 0,    # not used yet. maybe one day.
                                                               'id': id})

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
    Remove a profile-based query term.  Is an AJAX call.
    """
    terms = request.session.get("profilequery")
    del terms[int(id)]
    request.session['profilequery'] = terms
    return HttpResponseRedirect(reverse('profile_query'))
    
@permission_required('profiles')
def addgroup(request):
    """
    Add a group-based query term.  Is an AJAX call.
    
    Not implemented yet.  =)
    """
    return Http404
