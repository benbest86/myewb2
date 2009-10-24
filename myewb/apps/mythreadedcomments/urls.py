from django.conf.urls.defaults import patterns, url
from mythreadedcomments import views

urlpatterns = patterns('',
    ### Comments ###
    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/$', views.comment, name="tc_comment"),
    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/$', views.comment, name="tc_comment_parent"),
    url(r'^comment/(?P<object_id>\d+)/delete/$', views.comment_delete, name="tc_comment_delete"),
    url(r'^comment/(?P<edit_id>\d+)/edit/$', views.comment, name="tc_comment_edit"),
    
    ### Comments (AJAX) ###
    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<ajax>json|xml)/$', views.comment, name="tc_comment_ajax"),
    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/(?P<ajax>json|xml)/$', views.comment, name="tc_comment_parent_ajax"),
    url(r'^comment/(?P<edit_id>\d+)/edit/(?P<ajax>json|xml)/$', views.comment, name="tc_comment_edit_ajax"),
    
    url(r'^attach/$', views.get_attachment_form, name="ac_get_attachment_form"),
)