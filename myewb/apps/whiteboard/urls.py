# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings

from whiteboard import views

try:
    WIKI_URL_RE = settings.WIKI_URL_RE
except AttributeError:
    WIKI_URL_RE = r'[-\w]+'

urlpatterns = patterns('',
    url(r'^edit/(?P<title>'+ WIKI_URL_RE +r')/$', views.edit_article,
        name='wiki_edit'),

    url(r'^history/(?P<title>'+ WIKI_URL_RE +r')/$', views.article_history,
        name='wiki_article_history'),

    url(r'^history/(?P<title>'+ WIKI_URL_RE +r')/changeset/(?P<revision>\d+)/$', views.view_changeset,
        name='wiki_changeset',),

    url(r'^history/(?P<title>'+ WIKI_URL_RE +r')/revert/$', views.revert_to_revision,
        name='wiki_revert_to_revision'),
)
