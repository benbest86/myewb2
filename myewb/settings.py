# -*- coding: utf-8 -*-
# Django settings for complete pinax project.

import os.path
import sys
import posixpath
import pinax

PINAX_ROOT = os.path.realpath(os.path.dirname(pinax.__file__))
PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

# tells Pinax to use the default theme
PINAX_THEME = 'default'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# tells Pinax to serve media through django.views.static.serve.
SERVE_MEDIA = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'myewb2.db'       # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Eastern'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'media', 'static')

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = '/site_media/static/'
MEDIA_URL = STATIC_URL

# Additional directories which hold static files
STATICFILES_DIRS = (
    ('myewb', os.path.join(PROJECT_ROOT, 'media')),
    ('pinax', os.path.join(PINAX_ROOT, 'media', PINAX_THEME)),
)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'r6b801^aa5%)5cf5!&1z160o^u-!7^8kn**x5vsgvp^+7of&zg'

# Add the contribs directory to our path too
sys.path.insert(0, os.path.join(PROJECT_ROOT, "contrib"))

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    'dbtemplates.loader.load_template_source',
)

MIDDLEWARE_CLASSES = (
#    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django_openid.consumer.SessionConsumer',
    'account.middleware.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django_sorting.middleware.SortingMiddleware',
    'djangodblog.middleware.DBLogMiddleware',
    'pinax.middleware.security.HideSensistiveFieldsMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'siteutils.online_middleware.OnlineUsers',
    # 'djangologging.middleware.LoggingMiddleware',
    #'siteutils.helpers.SQLLogToConsoleMiddleware',
    #'siteutils.profile_middleware.ProfileMiddleware',
#    'django.middleware.cache.FetchFromCacheMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware'
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, "templates"),
    os.path.join(PINAX_ROOT, "templates", PINAX_THEME),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",

    "pinax.core.context_processors.pinax_settings",

#    "notification.context_processors.notification",
    "group_announcements.context_processors.site_wide_announcements",
#    "account.context_processors.openid",
    "account.context_processors.account",
    "messages.context_processors.inbox",
    "friends_app.context_processors.invitations",
    "context_processors.combined_inbox_count",
    "siteutils.context_processors.myewb_settings",
    "siteutils.context_processors.timezone",
    "siteutils.online_middleware.context",
    "group_topics.context_processors.newposts",
    "communities.context_processors.is_exec",
    "profiles.context_processors.toolbar_states",
)

COMBINED_INBOX_COUNT_SOURCES = (
    "messages.context_processors.inbox",
    "friends_app.context_processors.invitations",
#    "notification.context_processors.notification",
)

INSTALLED_APPS = (
    # included
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.formtools',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.markup',
    'pinax.templatetags',
    
    # external
#    'notification', # must be first
#    'django_openid',
    'emailconfirmation',
    'django_extensions',
    'robots',
    #'dbtemplates',
    'friends',
    'mailer',
    'messages',
    'messages_ext',
    'group_announcements',
    'oembed',
    #'djangodblog',
    'pagination',
#    'gravatar',
    'threadedcomments',
    'threadedcomments_extras',
    'mythreadedcomments',
    'wiki',
#    'swaps',
    'timezones',
    #'voting',
    #'voting_extras',
    'tagging',
    'tagging_utils',
    #'bookmarks',
    #'blog',
    'ajax_validation',
    #'photologue',
    'avatar',
    #'flag',
    #'microblogging',
    #'locations',
    'uni_form',
    'django_sorting',
    'django_markup',
#    'debug_toolbar',
    
    # internal (for now)
    'analytics',
    'profiles',
    'staticfiles',
    'account',
    'account_extra',
#    'misc',
    'signup_codes',
    #'tribes',
    #'photos',
    'tag_app',    
    'attachments',
    'topics',
    'group_topics',
    'groups',
    'base_groups',
    'networks',
    'communities',
    'creditcard',
    'conference',
    
    'django.contrib.admin',
    'events',
    'whiteboard',
    'siteutils',
    
    # MyEWB apps
    'volunteering',
    'siteutils',
    'manager_extras',
    'user_search',
    'permissions',
    'stats',
    'profile_query',
    'champ',
    'workspace',
    'mailchimp',
    'finance',
    'confcomm',

    # our own third-party libs
    'contrib.django_evolution',
    'contrib.haystack'
)

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/%s/" % o.username,
}

MARKUP_FILTER_FALLBACK = 'none'
MARKUP_CHOICES = (
    ('restructuredtext', u'reStructuredText'),
    ('textile', u'Textile'),
    ('markdown', u'Markdown'),
    ('creole', u'Creole'),
)
WIKI_MARKUP_CHOICES = MARKUP_CHOICES
DEFAULT_MAX_COMMENT_LENGTH = None

AUTH_PROFILE_MODULE = 'profiles.MemberProfile'
NOTIFICATION_LANGUAGE_MODULE = 'account.Account'

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_REQUIRED_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = True

DEFAULT_FROM_EMAIL = '"myEWB" <noreply@my.ewb.ca>'

EMAIL_CONFIRMATION_DAYS = 7
EMAIL_DEBUG = DEBUG
CONTACT_EMAIL = "info@my.ewb.ca"
SITE_NAME = "myEWB"
LOGIN_URL = "/account/login/"
LOGIN_REDIRECT_URLNAME = "home"

# probably want to make this memcached in local_settings for production use =) 
CACHE_BACKEND = 'dummy://'
#CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True      # will do user-based caching manually in the views
CACHE_MIDDLEWARE_KEY_PREFIX = ''
CACHE_TIMEOUT = 1800             # 30 minutes for internal queries
TEMPLATE_CACHE_TIMEOUT = 300             # 5 minutes for templates only

INTERNAL_IPS = (
    '127.0.0.1',
)

ugettext = lambda s: s
LANGUAGES = (
    ('en', u'English'),
#    ('fr', u'Français'),
)

# URCHIN_ID = "ua-..."

class NullStream(object):
    def write(*args, **kwargs):
        pass
    writeline = write
    writelines = write

RESTRUCTUREDTEXT_FILTER_SETTINGS = {
    'cloak_email_addresses': True,
    'file_insertion_enabled': False,
    'raw_enabled': False,
    'warning_stream': NullStream(),
    'strip_comments': True,
}

# if Django is running behind a proxy, we need to do things like use
# HTTP_X_FORWARDED_FOR instead of REMOTE_ADDR. This setting is used
# to inform apps of this fact
BEHIND_PROXY = False

FORCE_LOWERCASE_TAGS = True

WIKI_REQUIRES_LOGIN = True

# Uncomment this line after signing up for a Yahoo Maps API key at the
# following URL: https://developer.yahoo.com/wsregapp/
# YAHOO_MAPS_API_KEY = ''

# Useful stuff for credit card processing.  Note you will *need* to get
# your own merchant ID, and put it in local_settings.py
TD_MERCHANT_ID = None
TD_MERCHANT_URL = 'https://www.beanstream.com/scripts/process_transaction.asp'

# and if you want LDAP email-forwards support, define the info here.
# LDAP will fail silently otherwise.
LDAP_HOST = 'ldap://127.0.0.1'
LDAP_BIND_DN = 'cn=myewb,ou=accra,ou=services,dc=ewb,dc=ca'
LDAP_BIND_PW = ''

# set this to true if doing Google Apps integration, and be sure to override
# the values in local_settings
GOOGLE_APPS = False
GOOGLE_ADMIN = ""
GOOGLE_DOMAIN = ""
GOOGLE_PASSWORD = ""

# Mailchimp integration.  Leave set to None to disable (or replace in local_settings)
MAILCHIMP_KEY = None            # your API key with them
MAILCHIMP_LISTID = None         # the ID of the list you use
MAILCHIMP_CALLBACK_KEY = None   # a key to use for securing callbacks


# debug login
LOGGING_OUTPUT_ENABLED = True
LOGGING_LOG_SQL = True
LOGGING_OUTPUT_ENABLED = False

# django-haystack searching
HAYSTACK_SITECONF = 'myewb.search_sites'
HAYSTACK_SEARCH_ENGINE = 'dummy'
#HAYSTACK_SEARCH_ENGINE = 'whoosh'    # use this once you've installed the dependency
HAYSTACK_WHOOSH_PATH = os.path.join(PROJECT_ROOT, "myewb_index")
HAYSTACK_XAPIAN_PATH = os.path.join(PROJECT_ROOT, "myewb_index")

REALTIME_SEARCH = True

# scores for featured posts list
FEATURED_REPLY_SCORE = 20
FEATURED_VIEW_SCORE = 1

TEST_RUNNER = 'test_coverage.coverage_runner.run_tests'
from test_coverage.settings import *
COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'coverage_report')

# avatar controls
AVATAR_DEFAULT_URL =  MEDIA_URL + 'images/nophoto.gif'
AVATAR_GRAVATAR_BACKUP = False

CONF_HASH = ""
API_KEY = ""

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass
