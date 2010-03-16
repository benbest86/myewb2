import datetime
from haystack.indexes import *
from haystack import site
from events.models import Event


class EventIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    author = CharField(model_attr='owner')
    pub_date = DateTimeField(model_attr='start')

# not currently used; see apps/search/view.py, create_queryset()
#    def load_all_queryset(self):
#        return GroupTopic.objects.visible()

site.register(Event, EventIndex)
