from django import template

register = template.Library()

from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from siteutils import helpers
from events.models import Event
from events.views import timebound, filter_visibility
import settings

@register.inclusion_tag('events/tags/add.html')
def add_event_to(model_instance, css_id):
    ''' Tag instance with an event with dialog widget

    {% add_event_to myModel 'css_id' %}
    This is a javascript bit that requires jQuery.
    On pinax you may put it in extra_body.
    '''

    ContentType.objects.get_for_model(model_instance)
    obj_id = model_instance.id

    app_label = model_instance._meta.app_label
    model_name = model_instance._meta.module_name

    return locals()

@register.inclusion_tag('events/tags/add_link.html')
def event_link_add_to(model_instance, css_id, link_only=False):
    ''' Produce the link for add_event_to javascript

    {% event_link_add_to myModel 'css_id' %}
    '''

    app_label = model_instance._meta.app_label
    model_name = model_instance._meta.module_name

    return locals()

@register.inclusion_tag('events/tags/link_to_events_for.html')
def link_to_events_for(model_instance, css_class, link_only=False):
    ''' Produce the link to the events detail page

    {% link_to_events_for myModel 'css_class' %}
    '''

    if model_instance == None:
        app_label = None
        model_name = None
    else:
        app_label = model_instance._meta.app_label
        model_name = model_instance._meta.module_name

    return locals()

@register.inclusion_tag('events/tags/add_url.html')
def events_add_url(model_instance):
    ''' Produce the url to add events to a model

    {% events_add_url myModel %} might return something like:
    /events/add/auth/user/1/
    '''

    app_label = model_instance._meta.app_label
    model_name = model_instance._meta.module_name

    return locals()

@register.inclusion_tag('events/tags/upcoming.html')
def events_upcoming(user, model_instance):
    ''' Show upcoming events (in list format) for a given model
    '''
    
    if not helpers.is_visible(user, model_instance):
        return render_to_response('denied.html', context_instance=RequestContext(request))
        
    events = Event.objects.filter(content_type = ContentType.objects.get_for_model(model_instance),
                                  object_id = model_instance.id)
    events = events.filter(start__gte=datetime.today())
    events = events.order_by('start', 'end')
    events = events[:5]  # TODO: non-hard-code?

    return {"events": events}
    
@register.inclusion_tag('events/tags/upcoming_widget.html')
def events_widget(user):
    ''' Show upcoming events widget '''
    
    events = Event.objects.all()
    events = timebound(events)
    events = filter_visibility(events, user)

    return {"STATIC_URL": settings.STATIC_URL,
            "events": events}    

