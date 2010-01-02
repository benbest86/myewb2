"""myEWB profile template tags

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2009-06-30
Last modified: 2009-07-31
@author: Joshua Gorner, Francis Kung
"""
from django import template
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from profiles.forms import StudentRecordForm, WorkRecordForm, UserSearchForm
from profiles.models import StudentRecord, WorkRecord
from networks.models import Network

register = template.Library()

def show_profile(user):
    return {"user": user}
register.inclusion_tag("profiles/profile_item.html")(show_profile)

def clear_search_url(request):
    getvars = request.GET.copy()
    if 'search' in getvars:
        del getvars['search']
    if len(getvars.keys()) > 0:
        return "%s?%s" % (request.path, getvars.urlencode())
    else:
        return request.path
register.simple_tag(clear_search_url)

def show_student_records(user, is_me):
    """Used with the student_records template to display all of the user's student records."""
    records = StudentRecord.objects.filter(user=user)
    return {"user": user, "records": records, "is_me": is_me}
register.inclusion_tag("profiles/student_records.html")(show_student_records)

def show_student_records_js(user, is_me):
    """Used with the above function, but called from the javascript block"""
    """ does this result in a second db query? that'd be bad =( can we save the list from above? """
    records = StudentRecord.objects.filter(user=user)
    return {"user": user, "records": records, "is_me": is_me}
register.inclusion_tag("profiles/student_records_js.html")(show_student_records_js)

def show_work_records(user, is_me):
    """Used with the work_records template to display all of the user's work records."""
    records = WorkRecord.objects.filter(user=user)
    return {"user": user, "records": records, "is_me": is_me}
register.inclusion_tag("profiles/work_records.html")(show_work_records)

def show_work_records_js(user, is_me):
    """See above"""
    records = WorkRecord.objects.filter(user=user)
    return {"user": user, "records": records, "is_me": is_me}
register.inclusion_tag("profiles/work_records_js.html")(show_work_records_js)

def show_profile_search(search_terms):
    """Load and show the profile search box (really, only here for consistency)"""
    return {"search_terms": search_terms}
register.inclusion_tag("profiles/profile_search.html")(show_profile_search)

def show_user_search(field):
    """Load and show the user search widget"""
    chapters = Network.objects.filter(chapter_info__isnull=False)
    form = UserSearchForm(prefix=field, chapters=chapters)
    return {"user_search_form": form, "field": field}
register.inclusion_tag("profiles/user_search_ajax.html")(show_user_search)

def get_selected_user(user, field):
    return {"user": user, "field": field}
register.inclusion_tag("profiles/selected_user.html")(get_selected_user)

# These may be useful down the road, specifically if we have time to develop a means of dynamically
# fetching record forms

# def do_get_student_record_form(parser, token):
#     try:
#         tag_name, as_, context_name = token.split_contents()
#     except ValueError:
#         tagname = token.contents.split()[0]
#         raise template.TemplateSyntaxError, "%(tagname)r tag syntax is as follows: {%% %(tagname)r as VARIABLE %%}" % locals()
#     return StudentRecordFormNode(context_name)
# 
# class StudentRecordFormNode(template.Node):
#     def __init__(self, context_name):
#         self.context_name = context_name
#     def render(self, context):
#         context[self.context_name] = StudentRecordForm()
#         return ''
# 
# register.tag('get_student_record_form', do_get_student_record_form)
# 
# def do_get_work_record_form(parser, token):
#     try:
#         tag_name, as_, context_name = token.split_contents()
#     except ValueError:
#         tagname = token.contents.split()[0]
#         raise template.TemplateSyntaxError, "%(tagname)r tag syntax is as follows: {%% %(tagname)r as VARIABLE %%}" % locals()
#     return WordRecordFormNode(context_name)
# 
# class WorkRecordFormNode(template.Node):
#     def __init__(self, context_name):
#         self.context_name = context_name
#     def render(self, context):
#         context[self.context_name] = WorkRecordForm()
#         return ''
# 
# register.tag('get_work_record_form', do_get_work_record_form)
