
from django.conf.urls.defaults import *


# place app url patterns here

urlpatterns = patterns('confcomm.views',
        ('.*', 'legacy'),
)
