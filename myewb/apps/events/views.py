from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object, delete_object,\
        update_object
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.db.models import Q
from django.template import RequestContext

from base_groups.models import BaseGroup
from events.models import Event
from events.forms import EventForm, GroupEventForm#, EventAddForm
from wiki.models import Article

from django.contrib.auth.models import User

from datetime import datetime

from siteutils import helpers

def timebound(events, year=None, month=None, day=None, user=None):
    """
    Restrict events list to the specified time period.  If month or year are
    blank, assume the current month/year... but if day is blank, show all 
    events for the month.
    """
    
    # cast year, month, and day to int to strip leading zeros
    if year:
        events = events.filter(start__year=int(year))
    else:
        events = events.filter(start__year=datetime.today().year)
        
    if month:
        events = events.filter(start__month=int(month))
    else:
        events = events.filter(start__month=datetime.today().month)
        
    if day:
        events = events.filter(start__day=int(day))
        
    return events

# filter a list of events, returning only visible ones
def filter_visibility(events, user):
    """
    TODO: efficiency gains will be needed as the number of events increase...
    iterating through the entire list to check for visibility in the app is
    *not* scalable - eventually this will need to be done on a database level.
    For now, though (no more than ~50 events/month total in current myewb db)
    it's OK.
    """

    visible_events = []
    
    for event in events:
        parent = helpers.get_obj(ct=event.content_type, id=event.object_id)
        if helpers.is_visible(user, parent):
            visible_events.append(event)
    
    return visible_events
    
def all(request, year=None, month=None, day=None):
    events = Event.objects.all()
    events = timebound(events, year, month, day, request.user)
    events = filter_visibility(events, request.user)
    
    if day:
        templatename = "events/events_for_day.html"
    else:
        templatename = "events/event_list.html"
        
    return render_to_response( templatename,
                               { 'events': events,
                                 'parent':None,
                                 'year':year,
                                 'month':month,
                                 'day':day
                               },
                               context_instance=RequestContext(request),
                             )
 
def detail(request, id, slug):

    event = get_object_or_404(Event, pk=id)

    parent = helpers.get_obj(ct=event.content_type, id=event.object_id)
    if not helpers.is_visible(request.user, parent):
        return render_to_response('denied.html', context_instance=RequestContext(request))

    # create whiteboard if needed
    member = False
    if event.whiteboard == None:
        # this will fail if the event's parent is not a group... 
        # so, only events attached to a group can have a whiteboard.
        try:
            method = getattr(event.content_object, "associate")
            wb = Article(title="Event%d" % (event.id), content="")
            event.content_object.associate(wb, commit=False)
            wb.save()
            event.whiteboard = wb
            event.save()
            
            # FIXME: we assume if you can see the event, you can edit it
            member = True
        except:
            pass

    return render_to_response("events/event_detail.html",
                               { 'object': event,
                                'member': member,
                               },
                               context_instance=RequestContext(request),
                             )
 
@login_required
def delete(request, id):
    e = get_object_or_404(Event, pk=id)

    # TODO: group admins can delete too, not just event owners!
    if e.owner == request.user:

        return delete_object(request,
                model=Event,
                object_id = id,
                post_delete_redirect=reverse('events_all'),
        )

    else:
        return render_to_response('denied.html', context_instance=RequestContext(request))

@login_required
def create(request):

    return create_object(request,
        form_class=EventForm,
    )

@login_required
def add_choose_group(request):
    """
    Let someone choose a group, before creating an event...
    """
    if request.method == 'POST':
        group = request.POST.get('group', None)
        if group == "0":
            return add(request, 'auth', 'user', request.user.pk)
        else:
            type = group[0:1]
            groupid = group[1:]
            
            if type == 'n':
                return add(request, 'networks', 'network', groupid)
            elif type == 'c':
                return add(request, 'communities', 'community', groupid)
            else:
                # ???
                pass
    form = GroupEventForm(user=request.user)

    context = { 'form':form }
    context.update(locals())

    return render_to_response('events/events_add.html', context,\
            context_instance = RequestContext(request))

@login_required
def add(request, app_label, model_name, id):
    ''' Tag an event to another model object '''

    try:
        ct = ContentType.objects.get(\
                app_label = app_label,
                model = model_name)
        obj = ct.get_object_for_this_type( id=id )

    except:
        return HttpResponseNotFound()
    
    # visibility check
    if not helpers.is_visible(request.user, obj):
        return render_to_response('denied.html', context_instance=RequestContext(request))

    if request.method == 'POST':
        #request.POST.update( { 'owner':request.user.id, 'object_id':id,
        #        'content_type':ct.id, 'content_obj': obj, } )
        form = EventForm(request.POST)

        if form.is_valid():
            ev = form.save(commit=False)
            ev.owner = request.user
            ev.object_id = obj.id
            ev.content_type = ct
            ev.save()

            return HttpResponseRedirect(ev.get_absolute_url())
    else:
        form = EventForm()

    context = { 'form':form, 'object':obj, 'content_type':ct, }
    context.update(locals())

    return render_to_response('events/events_add.html', context,\
            context_instance = RequestContext(request))

@login_required
def change(request, id):
    # visibility check
    event = get_object_or_404(Event, pk=id)
    parent = helpers.get_obj(ct=event.content_type, id=event.object_id)
    if not helpers.is_visible(request.user, parent):
        return render_to_response('denied.html', context_instance=RequestContext(request))
    
    return update_object(request,
        form_class=EventForm,
        object_id = id,
    )

def for_user(request, username, year=None, month=None, day=None):
    ''' Returns response with all the events owned by or associated with a user

    '''

    user = get_object_or_404(User, username=username)
    events = Event.objects.filter(
            (Q(object_id=user.id)
                &
                Q(content_type=ContentType.objects.get_for_model(user))
            )|
            Q(owner=user)
    )
    
    events = timebound(events, year, month, day)
    # visibility check not needed - implicit (only finding events owned by user)
    
    if day:
        templatename = "events/events_for_day.html"
    else:
        templatename = "events/event_list.html"

    return render_to_response( templatename,
                               { 'events': events,
                                 'parent':user,
                                 'year':year,
                                 'month':month,
                                 'day':day
                               },
                               context_instance=RequestContext(request),
                             )

def for_instance(request, app_label, model_name, id, year=None, month=None, day=None):
    ''' Returns the events associated with the model instance

    '''

    obj = helpers.get_obj(app_label=app_label, model_name=model_name, id=id )
    if not helpers.is_visible(request.user, obj):
        return render_to_response('denied.html', context_instance=RequestContext(request))
        
    events = Event.objects.filter(content_type = ContentType.objects.get_for_model(obj), object_id = id)
    events = timebound(events, year, month, day)
        
    if day:
        templatename = "events/events_for_day.html"
    else:
        templatename = "events/event_list.html"

    return render_to_response( templatename,
                               { 'events': events,
                                 'parent':obj,
                                 'year':year,
                                 'month':month,
                                 'day':day
                               },
                               context_instance=RequestContext(request),
                             )
