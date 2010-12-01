import datetime
import settings
from haystack.indexes import *
from haystack import site
from whiteboard.models import Whiteboard

if settings.REALTIME_SEARCH:
    index_class = RealTimeSearchIndex
else:
    index_class = SearchIndex

class WhiteboardIndex(index_class):
    text = CharField(document=True, model_attr='content')
    
    def get_updated_field(self):
        return 'last_update'

# not currently used; see apps/search/view.py, create_queryset()
#    def load_all_queryset(self):
#        return GroupTopic.objects.visible()

site.register(Whiteboard, WhiteboardIndex)
