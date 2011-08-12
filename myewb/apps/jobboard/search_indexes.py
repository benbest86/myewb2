import datetime
import settings
from haystack.indexes import *
from haystack import site
from jobboard.models import *

if settings.REALTIME_SEARCH:
    index_class = RealTimeSearchIndex
else:
    index_class = SearchIndex

class JobBoardIndex(index_class):
    text = CharField(document=True, use_template=True)
    author = CharField(model_attr='owner')
    pub_date = DateTimeField(model_attr='posted_date')
    
    def index_queryset(self):
        return JobPosting.objects.open()
    
    def prepare_author(self, obj):
        return obj.owner.visible_name()
    
    def get_updated_field(self):
        return 'last_updated'

# not currently used; see apps/search/view.py, create_queryset()
#    def load_all_queryset(self):
#        return GroupTopic.objects.visible()

site.register(JobPosting, JobBoardIndex)
