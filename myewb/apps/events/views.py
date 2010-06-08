from vobject import iCalendar

import re
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object, delete_object,\
        update_object
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseNotFound, HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.db.models import Q
from django.template import RequestContext, Context, loader
from django.utils.translation import ugettext_lazy as _
from emailconfirmation.models import EmailAddress

from base_groups.models import BaseGroup
from events.models import Event
from events.forms import EventForm, GroupEventForm, EventEmailForm#, EventAddForm
from whiteboard.models import Whiteboard

from django.contrib.auth.models import User

from datetime import datetime, date

from siteutils import helpers
from siteutils.shortcuts import get_object_or_none

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

def upcoming(events):
    """
    Filter events to show upcoming events only.
    """
    return events.filter(start__gte=date.today())

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
        
    if request.GET.get("date", None):
        selected_date = request.GET['date']
        if re.match(r'^\d{4}/\d{2}/\d{2}$', selected_date) is None:    # validation
            selected_date = ""
    else:
        selected_date = ""
        
    return render_to_response( templatename,
                               { 'events': events,
                                 'parent':None,
                                 'year':year,
                                 'month':month,
                                 'day':day,
                                 'selected_date': selected_date
                               },
                               context_instance=RequestContext(request),
                             )
 
def detail(request, id, slug):

    event = get_object_or_404(Event, pk=id)

    parent = helpers.get_obj(ct=event.content_type, id=event.object_id)
    if not helpers.is_visible(request.user, parent):
        return render_to_response('denied.html', context_instance=RequestContext(request))

    can_edit = False
    can_send = False
    member = False
    # see if the parent object is a descendant of BaseGroup 
    if BaseGroup in parent.__class__.__bases__:
        can_edit = parent.user_is_admin(request.user)
        can_send = True
         
        # create whiteboard if needed
        if event.whiteboard == None:
            wb = Whiteboard(title="Event%d" % (event.id), content="")
            event.content_object.associate(wb, commit=False)
            wb.save()
            event.whiteboard = wb
            event.save()
            
        # we assume if you can see the event, you can edit it.  Is this intentional?
        member = True
        
    elif parent.__class__ == User:
        if parent == request.user:
            can_edit = True

    return render_to_response("events/event_detail.html",
                               { 'object': event,
                                'member': member,
                                'can_edit': can_edit,
                                'can_send': can_send
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
        form = GroupEventForm(request.POST, user=request.user)
        
        if form.is_valid(): 
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
            
    else:
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
    
    if request.method == 'POST':
        #request.POST.update( { 'owner':request.user.id, 'object_id':id,
        #        'content_type':ct.id, 'content_obj': obj, } )
        form = EventForm(request.POST, instance=event)

        if form.is_valid():
            ev = form.save()
            return HttpResponseRedirect(ev.get_absolute_url())
    else:
        form = EventForm(instance=event)

    context = { 'form':form, 'object':parent, 'content_type':event.content_type }
    context.update(locals())

    return render_to_response('events/events_add.html', context,\
            context_instance = RequestContext(request))

def for_user(request, username, year=None, month=None, day=None):
    ''' Returns response with all the events owned by or associated with a user

    '''
    user = get_object_or_404(User, username=username)
    
    if not request.user == user:
        return HttpResponseForbidden() 
    
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

def for_instance_slug(request, app_label, model_name, group_slug):
    obj = helpers.get_obj(app_label=app_label, model_name=model_name, slug=group_slug)
    return for_instance(request, app_label, model_name, id=obj.id)
    
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
                                 'day':day,
                                 'app_label': app_label,
                                 'model_name': model_name,
                               },
                               context_instance=RequestContext(request),
                             )

def feed_for_user(request, username, year=None, month=None, day=None):
    """
    Returns an ical feed of a user's events
    """
    user = get_object_or_404(User, username=username)
    
    # TODO: some API key way of allowing third-party access to a user's calendar?
    if not request.user == user:
        return HttpResponseForbidden() 
    
    events = Event.objects.filter(
            (Q(object_id=user.id)
                &
                Q(content_type=ContentType.objects.get_for_model(user))
            )|
            Q(owner=user)
    )
    
    events = timebound(events, year, month, day)
    # visibility check not needed - implicit (only finding events owned by user)

    return build_ical(events)

def feed_for_instance_slug(request, app_label, model_name, group_slug):
    obj = helpers.get_obj(app_label=app_label, model_name=model_name, slug=group_slug )
    return feed_for_instance(request, app_label, model_name, id=obj.id) 

def feed_for_instance(request, app_label, model_name, id, year=None, month=None, day=None):
    """
    Returns an ical feed of a group's events
    """
    obj = helpers.get_obj(app_label=app_label, model_name=model_name, id=id )
    if not helpers.is_visible(request.user, obj):
        return render_to_response('denied.html', context_instance=RequestContext(request))
        
    events = Event.objects.filter(content_type = ContentType.objects.get_for_model(obj), object_id = id)
    events = upcoming(events).order_by('start')[:30]
        
    return build_ical(events)

def feed_for_event(request, eventid):
    """
    Returns an ical export of a single event
    """
    event = get_object_or_404(Event, id=eventid)

    if not helpers.is_visible(request.user, event.content_object):
        return render_to_response('denied.html', context_instance=RequestContext(request))

    return build_ical([event])

def build_ical(events):
    ical = iCalendar()
    
    ical.add('method').value = 'PUBLISH'        # for IE/Outlook? http://blog.thescoop.org/archives/2007/07/31/django-ical-and-vobject/
    
    for e in events:
        vevent = ical.add('vevent')
        vevent.add('dtstart').value = e.start
        vevent.add('dtend').value = e.end
        vevent.add('uid').value = reverse('events_detail', kwargs={'id': e.pk, 'slug': e.slug})
        vevent.add('url').value = reverse('events_detail', kwargs={'id': e.pk, 'slug': e.slug})
        vevent.add('location').value = e.location
        vevent.add('summary').value = e.title
        vevent.add('description').value = e.description
    
    icalstream = ical.serialize()
    response = HttpResponse(icalstream, mimetype='text/calendar')
    response['Filename'] = 'myewb-events.ics'
    response['Content-Disposition'] = 'attachment; filename=myewb-events.ics'
    
    return response

def email_event(request, eventid):
    """
    Lets you email an event reminder.  Email goes to the parent group (if one exists).
    Later this would be great for "email all RSVPs" and such.
    """
    event = get_object_or_404(Event, id=eventid)
    parent = event.content_object
    
    if not helpers.is_visible(request.user, parent):
        return render_to_response('denied.html', context_instance=RequestContext(request))

    if BaseGroup not in parent.__class__.__bases__:
        request.user.message_set.create(message="You can only send emails to group-owned events.")
        return HttpResponseRedirect(reverse(event.get_absolute_url()))
    
    if not parent.user_is_admin(request.user): 
        request.user.message_set.create(message="You cannot send emails to the parent group.")
        return HttpResponseRedirect(reverse(event.get_absolute_url()))

    confirm = None
    if request.method == 'POST':
        form = EventEmailForm(request.POST, user=request.user, group=parent)
        
        if form.is_valid():
            if request.POST.get('confirmed', None) and request.POST.get('action', 'back') == "send":
                # extra security check that sender isn't forged.
                # can't hurt...
                # copied from group_topics.views.topics.new_topic - can we combine?
                sender_valid = False
                if parent.user_is_admin(request.user):
                    if form.cleaned_data['sender'] == parent.from_email:
                        sender_valid = True
                        sender = '"%s" <%s>' % (parent.from_name, parent.from_email)
                        
                    elif get_object_or_none(EmailAddress, email=form.cleaned_data['sender']) in request.user.get_profile().email_addresses():
                        sender_valid = True
                        sender = '"%s %s" <%s>' % (request.user.get_profile().first_name,
                                                   request.user.get_profile().last_name,
                                                   form.cleaned_data['sender'])
                        
                    elif request.user.is_staff and form.cleaned_data['sender'] == "info@ewb.ca":
                        sender_valid = True
                        sender = '"EWB-ISF Canada" <info@ewb.ca>'
                        
                # and this is all copied from group_topics.models.GroupTopic.send_email ... =(
                tmpl = loader.get_template("email_template.html")
                c = Context({'group': parent,
                             'title': form.cleaned_data['subject'],
                             'body': form.cleaned_data['body'],
                             'topic_id': None,
                             'event': event,
                             'attachments': None
                             })
                message = tmpl.render(c)
            
                parent.send_mail_to_members(form.cleaned_data['subject'], message, sender=sender)
                
                request.user.message_set.create(message="Email sent.")
                return HttpResponseRedirect(event.get_absolute_url())
            
            if not request.POST.get('action', None):
                confirm = request.POST
                
    else:
        form = EventEmailForm(user=request.user, group=parent)
        
    return render_to_response('events/email.html',
                               {'event': event,
                                'form': form,
                                'confirm': confirm
                               },
                               context_instance=RequestContext(request),
                             )

        