from django.conf import settings
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from haystack.forms import ModelSearchForm
from haystack.query import RelatedSearchQuerySet

from group_topics.models import GroupTopic
from whiteboard.models import Whiteboard

RESULTS_PER_PAGE = getattr(settings, 'HAYSTACK_SEARCH_RESULTS_PER_PAGE', 20)

def create_queryset(user):
    # ideally we'd do it this way, and not mention specific models here
    # (instead doing visibility checking in their respective search_index.py files),
    # but there's no way to pass a user into serach_index.load_all_queryset.  yet.
    #   
    # return RelatedSearchQuerySet()

    qs = RelatedSearchQuerySet().load_all_queryset(GroupTopic, GroupTopic.objects.visible(user))
    qs = qs.load_all_queryset(Whiteboard, Whiteboard.objects.visible(user))
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
    
    if request.GET.get('q'):
        form = ModelSearchForm(request.GET,
                               searchqueryset=qs,
                               load_all=True)
        
        if form.is_valid():
            query = form.cleaned_data['q']
            results = form.search()
    else:
        form = ModelSearchForm(searchqueryset=qs,
                               load_all=True)
        
    
    paginator = Paginator(results, RESULTS_PER_PAGE)
    
    try:
        page = paginator.page(int(request.GET.get('page', 1)))
    except InvalidPage:
        raise Http404("No such page of results!")
    
    context = {
        'form': form,
        'page': page,
        'paginator': paginator,
        'query': query,
    }
    
    return render_to_response("search/search.html", context, context_instance=RequestContext(request))
