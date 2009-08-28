from django.conf.urls.defaults import *

urlpatterns = patterns('networks.views.chapters',
    # Modified REST - only GET and POST used

    # GET - chapters index
    # POST - create chapter
    url(r'^$', 'chapters_index', name='chapters_index',),
    # GET - new chapter form
    # POST - create chapter (redirects to 'chapters_index'
    url(r'^new/$', 'new_chapter', name='new_chapter',),

    # GET - retrieve chapter detail
    # POST - update chapter
    url(r'^(?P<group_slug>[-\w]+)/$', 'chapter_detail', name='chapter_detail',),
    # GET - edit chapter form
    # POST - update chapter (redirects to 'chapter_detail'
    url(r'^(?P<group_slug>[-\w]+)/edit/$', 'edit_chapter', name='edit_chapter',),
    # POST - delete chapter
    url(r'^(?P<group_slug>[-\w]+)/delete/$', 'delete_chapter', name='delete_chapter',),
    )