import re, csv, codecs
encoder = codecs.getencoder("utf8")

from lxml.html.clean import clean_html, autolink_html, Cleaner

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_init
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from emailconfirmation.models import EmailAddress

def get_obj(app_label=None, model_name=None, ct=None, id=None, slug=None):
    """ 
    An error-handled way to get a generic object.
    You need to specify app_label and model_name, OR the ContentType object (ct)
      (if you supply a ct, the app_label and model_name will be ignored)
    And you also have to specify id OR slug
      (if you supply both, the id will be used)
    """
    try:
        if ct == None:
            ct = ContentType.objects.get(app_label = app_label,
                                         model = model_name)
        if id:
            obj = ct.get_object_for_this_type( pk=id )
        else:
            obj = ct.get_object_for_this_type( slug=slug )

    except:
        raise Http404('No object found. applabel %s | model %s | id %s' %
                      (app_label, model_name, id) )
    
    return obj

def is_visible(user, obj):
    """
    Checks the is_visible method of a generic obj, returning True if the obj
    doesn't have an is_visible method
    """

    try:
        method = getattr(obj, "is_visible")
        if not method(user):
            return False
        
    except:
        # the parent object didn't have an is_visible method defined -
        # assume global visibility (???)
        # for now shouldn't happen, as event.parent can only be a base_group
        # and threadedcomment.parent a grouptopic
        # (but this "keep track of where this is used" strategy won't work forever)
        pass
    
    return True

def get_email_user(email):
    email_user = None
    users_with_the_email = User.objects.filter(email=email)
    if users_with_the_email.count() > 0:
        email_user = users_with_the_email[0]
    else:
        users_with_the_email = EmailAddress.objects.get_users_for(email)
        if len(users_with_the_email) > 0:
            email_user = users_with_the_email[0]
            
    return email_user


from django.db import connection
from django.template import Template, Context
from django.conf import settings


#
# Log all SQL statements direct to the console (when running in DEBUG)
# Intended for use with the django development server.
#
class SQLLogToConsoleMiddleware:
    def process_response(self, request, response): 
        if settings.DEBUG and connection.queries:
            time = sum([float(q['time']) for q in connection.queries])
            clean_queries = []
            for q in connection.queries:
              if q['sql'].find("django_session") == -1:
                clean_queries.append(q)
            t = Template("{% load sql_keyword_filters %}{% autoescape off %}{% if count %}{{ count }} quer{{ count|pluralize:\"y,ies\" }} in {{ time }} seconds:\n\n{% for sql in sqllog %}[{{ forloop.counter }}] {{ sql.time }}s: {{ sql.sql|safe }}{% if not forloop.last %}\n\n{% endif %}{% endfor %}{% endif %}{% endautoescape %}")
            try:
                print t.render(Context({'sqllog':clean_queries,'count':len(clean_queries),'time':time}))
            except:
                print "unable to print query"                
        return response

# Duckpunch to add the "visible_name" function to the User obejct
def visible_name(self):
    if self.first_name and self.last_name:
        return "%s %s" % (self.first_name, self.last_name)
    elif self.first_name:
        return self.first_name
    elif self.last_name:
        return self.last_name
    elif self.email:
        return self.email.split('@')[0] + "@..."
    else:
        return "Unknown user (%s)" % self.username
        #return "Unknown user"
User.add_to_class("visible_name", visible_name)

def wiki_convert(text):
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    
    text = re.sub(r'-{4,}', "<hr/>", text)
    text = re.sub(r'={4,}', "<hr/>", text)

#    bold_exp = re.compile(r'(.*?)\*\*(.+?)\*\*(.*?)', re.S)
    bold_exp = re.compile(r'(.*?)\*{2,}(.+?)\*{2,}(.*?)', re.S)
    text = bold_exp.sub(r"\1<strong>\2</strong>\3", text)

#    italic_exp = re.compile(r'(.*?)\^\^(.+?)\^\^(.*?)', re.S)
    italic_exp = re.compile(r'(.*?)\^{2,}(.+?)\^{2,}(.*?)', re.S)
    text = italic_exp.sub(r"\1<em>\2</em>\3", text)

    heading_exp = re.compile(r'(.*?)={2,}(.+?)={2,}(.*?)', re.S)
    text = heading_exp.sub(r"\1<h3>\2</h3>\3", text)
    
    text = text.replace("\n", "<br/>")
    
    return text

email_re = re.compile(
    r"([-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?', re.IGNORECASE)  # domain

double_re = re.compile(
    r'<a href="mailto:<a href="mailto:(.*)">\1</a>"><a href="mailto:\1">\1</a></a>')

named_link_re = re.compile(
    r'<a href="mailto:<a href="mailto:(.*)">\1</a>">(.*)</a>')

def autolink_email(text):
    # do initial substitution
    text = email_re.sub('<a href="mailto:\g<0>">\g<0></a>', text)

    # but if it's been double-substituted, undo it...!
    text = double_re.sub('<a href="mailto:\g<1>">\g<1></a>', text)
    
    # and cover an editor-inserted named link
    text = named_link_re.sub('<a href="mailto:\g<1>">\g<2></a>', text)
    
    return text

def fix_encoding(text):
    try:
        return encoder(text)[0]
    except:
        return text

# Thanks to http://djangosnippets.org/snippets/1040/
from django.db.models import AutoField
def copy_model_instance(obj):
    initial = dict([(f.name, getattr(obj, f.name))
                    for f in obj._meta.fields
                    if not isinstance(f, AutoField) and\
                       not f in obj._meta.parents.values()])
    return obj.__class__(**initial)