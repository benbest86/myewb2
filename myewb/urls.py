from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.contrib import admin

from account.openid_consumer import PinaxConsumer

import os.path

#from microblogging.feeds import TweetFeedAll, TweetFeedUser, TweetFeedUserWithFriends
#tweets_feed_dict = {"feed_dict": {
#    'all': TweetFeedAll,
#    'only': TweetFeedUser,
#    'with_friends': TweetFeedUserWithFriends,
#}}
#
#from blog.feeds import BlogFeedAll, BlogFeedUser
#blogs_feed_dict = {"feed_dict": {
#    'all': BlogFeedAll,
#    'only': BlogFeedUser,
#}}
#
#from bookmarks.feeds import BookmarkFeed
#bookmarks_feed_dict = {"feed_dict": { '': BookmarkFeed }}

from group_topics.views.rss import RSSAllPosts
rss = {'posts': RSSAllPosts}

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'group_topics.views.topics.topics', {'template_name': 'frontpage.html'}, name="home"),

    (r'^volunteering/', include('volunteering.urls')),

    
    (r'^about/', include('about.urls')),
    (r'^account/', include('account_extra.urls')),
    (r'^auto/tags/', include('tagging_utils.urls')),
    (r'^openid/(.*)', PinaxConsumer()),
    (r'^bbauth/', include('bbauth.urls')),
    (r'^authsub/', include('authsub.urls')),
    (r'^profiles/', include('profiles.urls')),
    (r'^query/', include('profile_query.urls')),
#    (r'^blog/', include('blog.urls')),
    (r'^tags/', include('tag_app.urls')),
    (r'^invitations/', include('friends_app.urls')),
    #(r'^notices/', include('notification.urls')),
    (r'^messages/', include('messages_ext.urls')),
    (r'^announcements/', include('group_announcements.urls')),
    (r'^tweets/', include('microblogging.urls')),
    (r'^comments/', include('mythreadedcomments.urls')),
    (r'^robots.txt$', include('robots.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
#    (r'^bookmarks/', include('bookmarks.urls')),

    (r'^admin/jsi18n/$', 'django.views.i18n.javascript_catalog'),
    (r'^admin/(.*)', admin.site.root),
#    (r'^photos/', include('photos.urls')),
    (r'^avatar/', include('avatar.urls')),
#    (r'^swaps/', include('swaps.urls')),
    (r'^flag/', include('flag.urls')),
#    (r'^locations/', include('locations.urls')),
    
    (r'^groups/', include('base_groups.urls')),
    (r'^networks/', include('networks.urls.network')),
    (r'^chapters/', include('networks.urls.chapters')),
    (r'^communities/', include('communities.urls')),
    (r'^events/', include('events.urls')),
    (r'^posts/', include('group_topics.urls.topics')),
    (r'^creditcard/', include('creditcard.urls')),
    (r'^conference/', include('conference.urls')),
    (r'^usersearch/', include('user_search.urls')),
    (r'^permissions/', include('permissions.urls')),
    (r'^search/', include('search.urls')),
    (r'^stats/', include('stats.urls')),
    (r'^champ/', include('champ.urls')),
    (r'^workspace/', include('workspace.urls')),
    (r'^mailchimp/', include('mailchimp.urls')),
	(r'^finance/', include('finance.urls')),
	(r'^confcomm/', include('confcomm.legacy_urls')),
    
    url(r'^unsubscribe/$', 'networks.views.network.unsubscribe', name='network_unsubscribe',),
    
#    (r'^feeds/tweets/(.*)/$', 'django.contrib.syndication.views.feed', tweets_feed_dict),
#    (r'^feeds/posts/(.*)/$', 'django.contrib.syndication.views.feed', blogs_feed_dict),
#    (r'^feeds/bookmarks/(.*)/?$', 'django.contrib.syndication.views.feed', bookmarks_feed_dict),

    # these are atom feeds, not rss.  just in case that's a useful distinction.
    url(r'^feeds/posts/group/(?P<group_slug>[-\w]+)/$', 'group_topics.views.feed.group', name="topic_feed_group"),
    url(r'^feeds/posts/tag/(?P<tag>[-\w]+)/$', 'group_topics.views.feed.tag', name="topic_feed_tag"),
    url(r'^feeds/posts/featured/$', 'group_topics.views.feed.featured', name="topic_feed_featured"),
    url(r'^feeds/posts/all/$', 'group_topics.views.feed.all', name="topic_feed_all"),
    
    # only really for the Polar Mobile app... but hey, let's do RSS as well
    url(r'^rss/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': rss}), 
    
    url(r'^newpost/$', 'group_topics.views.topics.new_topic', name="topic_new"),
    
    # ajax keepalive call that also updates the whos-online bar
    url(r'^keepalive/$', direct_to_template, {"template": "whosonline.html"}, name="whosonline_refresh"),
    
    # legacy URLs from myEWB 1
    (r'^home/', include('legacy_urls.home')),
    (r'^profile/', include('legacy_urls.profile')),
    (r'^chapter/', include('legacy_urls.chapter')),
    (r'^mailing/', include('legacy_urls.mailing')),
    (r'^events/', include('legacy_urls.eventsurls')),
    #(r'^volunteering/', include('legacy_urls.volunteering')),
    (r'^api/', include('legacy_urls.api')),
    (r'^cal/', include('legacy_urls.cal')),
    (r'^actions/', include('legacy_urls.actions')),
    (r'^postfile/', include('legacy_urls.postfile')),
)

## @@@ for now, we'll use friends_app to glue this stuff together

#from photos.models import Image
#
#friends_photos_kwargs = {
#    "template_name": "photos/friends_photos.html",
#    "friends_objects_function": lambda users: Image.objects.filter(member__in=users),
#}
#
#from blog.models import Post
#
#friends_blogs_kwargs = {
#    "template_name": "blog/friends_posts.html",
#    "friends_objects_function": lambda users: Post.objects.filter(author__in=users),
#}
#
#from microblogging.models import Tweet
#
#friends_tweets_kwargs = {
#    "template_name": "microblogging/friends_tweets.html",
#    "friends_objects_function": lambda users: Tweet.objects.filter(sender_id__in=[user.id for user in users], sender_type__name='user'),
#}
#
#from bookmarks.models import Bookmark
#
#friends_bookmarks_kwargs = {
#    "template_name": "bookmarks/friends_bookmarks.html",
#    "friends_objects_function": lambda users: Bookmark.objects.filter(saved_instances__user__in=users),
#    "extra_context": {
#        "user_bookmarks": lambda request: Bookmark.objects.filter(saved_instances__user=request.user),
#    },
#}
#
#urlpatterns += patterns('',
#    url('^photos/friends_photos/$', 'friends_app.views.friends_objects', kwargs=friends_photos_kwargs, name="friends_photos"),
#    url('^blog/friends_blogs/$', 'friends_app.views.friends_objects', kwargs=friends_blogs_kwargs, name="friends_blogs"),
#    url('^tweets/friends_tweets/$', 'friends_app.views.friends_objects', kwargs=friends_tweets_kwargs, name="friends_tweets"),
#    url('^bookmarks/friends_bookmarks/$', 'friends_app.views.friends_objects', kwargs=friends_bookmarks_kwargs, name="friends_bookmarks"),
#)

if settings.SERVE_MEDIA:
    urlpatterns += patterns('', 
        (r'^site_media/', include('staticfiles.urls'))
    )
