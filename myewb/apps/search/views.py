"""myEWB searching views

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

Created on: 2010-03-17
@author: Francis Kung
"""

from django.conf import settings
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from haystack.query import RelatedSearchQuerySet

from champ.models import Activity
from group_topics.models import GroupTopic
from whiteboard.models import Whiteboard
from events.models import Event
from communities.models import Community
from search.forms import DateAuthorSearchForm
from siteutils.shortcuts import get_object_or_none

def create_queryset(user):
    # ideally we'd do it this way, and not mention specific models here
    # (instead doing visibility checking in their respective search_index.py files),
    # but there's no way to pass a user into serach_index.load_all_queryset.  yet.
    #   
    # return RelatedSearchQuerySet()

    qs = RelatedSearchQuerySet().load_all_queryset(GroupTopic, GroupTopic.objects.visible(user))
    qs = qs.load_all_queryset(Whiteboard, Whiteboard.objects.visible(user))
    qs = qs.load_all_queryset(Event, Event.objects.visible(user))

    # TODO: centralize this somewhere?
    execlist = get_object_or_none(Community, slug='exec')
    if execlist and execlist.user_is_member(user, True):
        qs = qs.load_all_queryset(Activity, Activity.objects.all())
    else:
        qs = qs.load_all_queryset(Activity, Activity.objects.none())
        
    return qs

def search(request):
    """
    A more traditional view that also demonstrate an alternative
    way to use Haystack.
    
    Useful as an example of for basing heavily custom views off of.
    
    Also has the benefit of thread-safety, which the ``SearchView`` class may
    not be.
    
    Template:: ``search/search.html``
    Context::
        * form
          An instance of the ``form_class``. (default: ``ModelSearchForm``)
        * page
          The current page of search results.
        * paginator
          A paginator instance for the results.
        * query
          The query received by the form.
    """
    query = ''
    results = []
    qs = create_queryset(request.user)
    
    form = DateAuthorSearchForm(request.GET,
                           searchqueryset=qs,
                           load_all=True)
    
    if form.is_valid():
        results = form.search()
    
    context = {
        'form': form,
        'results': results,
    }
    
    return render_to_response("search/search.html", context, context_instance=RequestContext(request))
