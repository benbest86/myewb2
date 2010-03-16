import datetime
from haystack.indexes import *
from haystack import site
from group_topics.models import GroupTopic


class GroupTopicIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    author = CharField(model_attr='creator')
    pub_date = DateTimeField(model_attr='created')

# not currently used; see apps/search/view.py, create_queryset()
#    def load_all_queryset(self):
#        return GroupTopic.objects.visible()

site.register(GroupTopic, GroupTopicIndex)
