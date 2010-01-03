from django.conf.urls.defaults import *
from messages_ext.views import compose


# import all the URLs from the stock messaging app
from messages import urls

# this is the only URL we want to override
urlpatterns = patterns('',
                       url(r'^compose/$', compose, name='messages_compose')
)

# and prepend our URL to the list, so ours is hit first
urlpatterns = urlpatterns + urls.urlpatterns
