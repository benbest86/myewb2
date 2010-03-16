import datetime
from haystack.indexes import *
from haystack import site
from whiteboard.models import Whiteboard


class WhiteboardIndex(SearchIndex):
    text = CharField(document=True, model_attr='content')

# not currently used; see apps/search/view.py, create_queryset()
#    def load_all_queryset(self):
#        return GroupTopic.objects.visible()

site.register(Whiteboard, WhiteboardIndex)
