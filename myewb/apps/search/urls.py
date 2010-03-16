from django.conf.urls.defaults import *

urlpatterns = patterns('search.views',
    url(r'^$', view='search', name='search'),
)
