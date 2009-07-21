"""myEWB profile views
Functions used to display additional (or replacement) profile-related views not provided by Pinax's profiles app.

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2009-06-22
Last modified: 2009-07-21
@author: Joshua Gorner
"""

from django.shortcuts import get_object_or_404
from pinax.apps.profiles.views import *
from profiles.models import StudentRecord, WorkRecord
from profiles.forms import StudentRecordForm, WorkRecordForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def add_student_record(request, username, template_name="profiles/add_student_record.html"):
	"""Used to add a new student record.
	"""
	return student_record(request, username, None, template_name)

def student_record(request, username, record_id, template_name="profiles/edit_student_record.html"):
    """Used to add or modify the user's student records."""
    
    user = request.user
    record = None
    if record_id:
        record = get_object_or_404(StudentRecord, id=record_id)
        if not user == record.user:
            # User should not be able to edit another user's record
            return HttpResponseRedirect(reverse('profile_detail', args=(record.user.username,)))
    elif not username == user.username:
        # User should not be able to create a record for another user
        return HttpResponseRedirect(reverse('profile_detail', args=(username,)))
    
    if request.method == "POST":
        if request.POST["action"] == "add":
            record_form = StudentRecordForm(request.POST)
            if record_form.is_valid():
                record = record_form.save(commit=False)
                record.user = user
                record.save()
                return HttpResponseRedirect(reverse('profile_detail', args=(user.username,)))
        elif request.POST["action"] == "update" and record:
            record_form = StudentRecordForm(request.POST, instance=record)
            if record_form.is_valid():
                record = record_form.save(commit=False)
                record.user = user
                record.save()
                return HttpResponseRedirect(reverse('profile_detail', args=(user.username,)))
        else:
            record_form = StudentRecordForm()
    else:
        record_form = StudentRecordForm(instance=record)

    return render_to_response(template_name, {
        "record_form": record_form,
    }, context_instance=RequestContext(request))
        
def add_work_record(request, username, template_name="profiles/add_work_record.html"):
	"""Used to add a new work record."""
	return work_record(request, username, None, template_name)

def work_record(request, username, record_id, template_name="profiles/edit_work_record.html"):
    """Used to add or modify the user's work records."""

    user = request.user
    record = None
    if record_id:
        record = get_object_or_404(WorkRecord, id=record_id)
        if not user == record.user:
            # User should not be able to edit another user's record
            return HttpResponseRedirect(reverse('profile_detail', args=(record.user.username,)))
    elif not username == user.username:
        # User should not be able to create a record for another user
        return HttpResponseRedirect(reverse('profile_detail', args=(username,)))

    if request.method == "POST":
        if request.POST["action"] == "add":
            record_form = WorkRecordForm(request.POST)
            if record_form.is_valid():
                record = record_form.save(commit=False)
                record.user = user
                record.save()
                return HttpResponseRedirect(reverse('profile_detail', args=(user.username,)))
        elif request.POST["action"] == "update" and record:
            record_form = WorkRecordForm(request.POST, instance=record)
            if record_form.is_valid():
                record = record_form.save(commit=False)
                record.user = user
                record.save()
                return HttpResponseRedirect(reverse('profile_detail', args=(user.username,)))
        else:
            record_form = WorkRecordForm()
    else:
        record_form = WorkRecordForm(instance=record)

    return render_to_response(template_name, {
        "record_form": record_form,
    }, context_instance=RequestContext(request))