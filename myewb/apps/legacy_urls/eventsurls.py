from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse

urlpatterns = patterns('django.views.generic.simple',
    url(r'^Events', 'redirect_to', {'url': reverse('events_all'),
                                    'permanent': True}),
    url(r'^MonthView', 'redirect_to', {'url': reverse('events_all'),
                                    'permanent': True}),
    url(r'^EditEvent', 'redirect_to', {'url': reverse('events_all'),
                                    'permanent': True}),
    url(r'^DayView', 'redirect_to', {'url': reverse('events_all'),
                                    'permanent': True}),
    url(r'^EventInfo', 'redirect_to', {'url': reverse('events_all'),
                                    'permanent': True}),
    url(r'^Conference', 'redirect_to', {'url': reverse('events_all'),
                                    'permanent': True}),
    url(r'^EditWhiteboard', 'redirect_to', {'url': reverse('events_all'),
                                    'permanent': True}),
    url(r'^ListView', 'redirect_to', {'url': reverse('events_all'),
                                    'permanent': True}),
    url(r'^ListUpcoming', 'redirect_to', {'url': reverse('events_all'),
                                    'permanent': True}),
    url(r'^TopKeywords', 'redirect_to', {'url': reverse('events_all'),
                                    'permanent': True}),
    )
