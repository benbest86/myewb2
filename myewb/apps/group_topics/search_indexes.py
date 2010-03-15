import datetime
from haystack.indexes import *
from haystack import site
from group_topics.models import GroupTopic


class GroupTopicIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    author = CharField(model_attr='creator')
    pub_date = DateTimeField(model_attr='created')

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return GroupTopic.objects.all()


site.register(GroupTopic, GroupTopicIndex)