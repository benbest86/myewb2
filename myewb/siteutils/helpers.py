from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
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
        # for now shouldn't happen, as event.parent can only be a baes_group
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
            t = Template("{% load sql_keyword_filters %}{% autoescape off %}{% if count %}{{ count }} quer{{ count|pluralize:\"y,ies\" }} in {{ time }} seconds:\n\n{% for sql in sqllog %}[{{ forloop.counter }}] {{ sql.time }}s: {{ sql.sql|safe|colorsql }}{% if not forloop.last %}\n\n{% endif %}{% endfor %}{% endif %}{% endautoescape %}")
            print t.render(Context({'sqllog':clean_queries,'count':len(clean_queries),'time':time}))                
        return response
