from django.conf.urls.defaults import *
from mailchimp.views import callback

urlpatterns = patterns('',
                       url(r'^$', callback, name='mailchimp_callback')
)
