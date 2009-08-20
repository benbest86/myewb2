from django.conf.urls.defaults import *

urlpatterns = patterns('ideas_app.views',
        url(r'^$', 'ideas_index', name='ideas_index'),
        url(r'^(?P<idea_id>\d+)/$', 'idea_detail', name='idea_detail'),
        url(r'^(?P<idea_id>\d+)/new/$', 'new_idea', name='new_idea'),
        url(r'^(?P<idea_id>\d+)/edit/$', 'edit_idea', name='edit_idea'),
        url(r'^(?P<idea_id>\d+)/delete/$', 'delete_idea', name='delete_idea'),
        url(r'^(?P<idea_id>\d+)/up/$', 'upvote_idea', name='upvote_idea'),
        url(r'^(?P<idea_id>\d+)/down/$', 'downvote_idea', name='downvote_idea'),
)
