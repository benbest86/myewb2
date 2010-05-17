import datetime
import settings
from haystack.indexes import *
from haystack import site
from threadedcomments.models import ThreadedComment

if settings.REALTIME_SEARCH:
    index_class = RealTimeSearchIndex
else:
    index_class = SearchIndex

class CommentsIndex(index_class):
    text = CharField(document=True, use_template=True)
    author = CharField(model_attr='user')
    pub_date = DateTimeField(model_attr='date_submitted')
    
    def prepare_author(self, obj):
        return obj.user.visible_name()

# not currently used; see apps/search/view.py, create_queryset()
#    def load_all_queryset(self):
#        return GroupTopic.objects.visible()

site.register(ThreadedComment, CommentsIndex)
