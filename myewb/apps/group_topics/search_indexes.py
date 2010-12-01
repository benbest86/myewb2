import datetime
import settings
from haystack.indexes import *
from haystack import site
from group_topics.models import GroupTopic

if settings.REALTIME_SEARCH:
    index_class = RealTimeSearchIndex
else:
    index_class = SearchIndex

class GroupTopicIndex(index_class):
    text = CharField(document=True, use_template=True)
    author = CharField(model_attr='creator')
    pub_date = DateTimeField(model_attr='created')
    
    def prepare_author(self, obj):
        return obj.creator.visible_name()
    
    def get_updated_field(self):
        return 'last_reply'

# not currently used; see apps/search/view.py, create_queryset()
#    def load_all_queryset(self):
#        return GroupTopic.objects.visible()

site.register(GroupTopic, GroupTopicIndex)
