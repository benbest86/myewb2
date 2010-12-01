import datetime
import settings
from haystack.indexes import *
from haystack import site
from events.models import Event

if settings.REALTIME_SEARCH:
    index_class = RealTimeSearchIndex
else:
    index_class = SearchIndex

class EventIndex(index_class):
    text = CharField(document=True, use_template=True)
    author = CharField(model_attr='owner')
    pub_date = DateTimeField(model_attr='start')

    def prepare_author(self, obj):
        return obj.owner.visible_name()

    def get_updated_field(self):
        return 'modified_date'

# not currently used; see apps/search/view.py, create_queryset()
#    def load_all_queryset(self):
#        return GroupTopic.objects.visible()

site.register(Event, EventIndex)
