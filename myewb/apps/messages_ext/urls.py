from django.conf.urls.defaults import *
from messages_ext.views import compose, reply


# import all the URLs from the stock messaging app
from messages import urls

# we want to override the URLs that provide a composition form
urlpatterns = patterns('',
                       url(r'^compose/$', compose, name='messages_compose'),
                       url(r'^compose/(?P<recipient>[\+\w]+)/$', compose, name='messages_compose_to'),
                       url(r'^reply/(?P<message_id>[\d]+)/$', reply, name='messages_reply'),
)

# and prepend our URL to the list, so ours is hit first
urlpatterns = urlpatterns + urls.urlpatterns
