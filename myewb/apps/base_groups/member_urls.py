# NOT ACTUALLY USED AT PRESENT

from django.conf.urls.defaults import *

urlpatterns = patterns('base_groups.member_views',
    # Modified REST - only GET and POST used

    # GET - members index
    # POST - create member
    url(r'^members/$', 'members_index', name='members_index',),
    # GET - new member form
    # POST - create member (redirects to 'members_index'
    url(r'^members/new/$', 'new_member', name='new_member',),

    # GET - retrieve member detail
    # POST - update member
    url(r'^members/(?P<username>[\w\._-]+)/$', 'member_detail', name='member_detail',),
    # GET - edit member form
    # POST - update member (redirects to 'member_detail'
    url(r'^members/(?P<username>[\w\._-]+)/edit/$', 'edit_member', name='edit_member',),
    # POST - delete member
    url(r'^members/(?P<username>[\w\._-]+)/delete/$', 'delete_member', name='delete_member',),
)