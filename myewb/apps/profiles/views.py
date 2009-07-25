"""myEWB profile views
Functions used to display additional (or replacement) profile-related views not provided by Pinax's profiles app.

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2009-06-22
Last modified: 2009-07-21
@author: Joshua Gorner, Francis Kung, Ben Best
"""

from django.shortcuts import get_object_or_404
from pinax.apps.profiles.views import *
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from siteutils.decorators import owner_required
from profiles.models import MemberProfile, StudentRecord, WorkRecord
from profiles.forms import StudentRecordForm, WorkRecordForm, ProfileSearchForm

def student_records_index(request, username, template_name='profiles/student_records_index.html'):
    if request.method == 'POST':
        return create_student_record(request, username=username)
    other_user = get_object_or_404(User, username=username)
    student_records = StudentRecord.objects.filter(user=other_user)
    return render_to_response(
            template_name,
            {
                'student_records': student_records,
                'other_user': other_user,
                },
            )

@owner_required(MemberProfile)
def create_student_record(request, username, object=None):
    form = StudentRecordForm(request.POST)
    other_user = User.objects.get(username=username)
    if form.is_valid():
        student_record = form.save(commit=False)
        student_record.user = other_user
        student_record.save()
        return HttpResponseRedirect(reverse('profile_detail', kwargs={'username': other_user.username }))
        
    else:
        return render_to_response(
                'profiles/new_student_record.html',
                {
                'form': form,
                'other_user': other_user,
                },
                context_instance=RequestContext(request)
                )

@owner_required(MemberProfile)
def new_student_record(request, username, template_name='profiles/new_student_record.html', object=None):
    # Handle POST to new as a create request
    if request.method == 'POST':
        return student_records_index(request, username)
    other_user = get_object_or_404(User, username=username)
    form = StudentRecordForm()
    return render_to_response(
            template_name,
            {
            'form': form,
            'other_user': other_user,
            },
            context_instance=RequestContext(request)
            )

def student_record_detail(request, username, student_record_id, template_name='profiles/student_record_detail.html'):
    if request.method == 'POST':
        return update_student_record(request, username=username, student_record_id=student_record_id)
    other_user = get_object_or_404(User, username=username)
    student_record = get_object_or_404(StudentRecord, id=student_record_id)
    return render_to_response(
            template_name,
            {
                'student_record': student_record,
                'other_user': other_user,
            },
            context_instance=RequestContext(request)
            )
    return get_student_record(request, **kwargs)

@owner_required(StudentRecord)
def update_student_record(request, username, student_record_id, object=None):
    if object:
        student_record = object
    else:
        student_record = get_object_or_404(StudentRecord, id=student_record_id)
    form = StudentRecordForm(request.POST, instance=student_record)
    other_user = User.objects.get(username=username)

    # if form saves, redirect to profile_detail
    if form.is_valid():
        student_record = form.save(commit=False)
        student_record.user = other_user
        student_record.save()
        return HttpResponseRedirect(reverse('profile_detail', kwargs={'username': other_user.username }))
        # if save fails, go back to edit_resource page
    else:
        return render_to_response(
                'profiles/edit_student_record.html',
                {
                    'form': form,
                    'student_record': student_record,
                    'other_user': other_user,
                },
                context_instance=RequestContext(request)
                )


@owner_required(StudentRecord)
def edit_student_record(request, username, student_record_id, template_name='profiles/edit_student_record.html', object=None):
    if request.method == 'POST':
        return update_student_record(request, username=username, student_record_id=student_record_id, object=object)
    other_user = get_object_or_404(User, username=username)
    if object:
        student_record = object
    else:
        student_record = get_object_or_404(StudentRecord, id=student_record_id)
    form = StudentRecordForm(instance=student_record)
    return render_to_response(
            template_name,
            {
                'form': form,
                'student_record': student_record,
                'other_user': other_user,
            },
            context_instance=RequestContext(request)
            )

@owner_required(StudentRecord)
def delete_student_record(request, username, student_record_id, object=None):
    if object:
        student_record = object
    else:
        student_record = get_object_or_404(StudentRecord, id=student_record_id)
    if request.method == 'POST':
        student_record.delete()
        return HttpResponseRedirect(reverse('student_record_index', kwargs={'username': username}))
        
def work_records_index(request, username, template_name='profiles/work_records_index.html'):
    if request.method == 'POST':
        return create_work_record(request, username=username)
    other_user = get_object_or_404(User, username=username)
    work_records = WorkRecord.objects.filter(user=other_user)
    return render_to_response(
            template_name,
            {
                'work_records': work_records,
                'other_user': other_user,
                },
            )

@owner_required(MemberProfile)
def create_work_record(request, username, object=None):
    form = WorkRecordForm(request.POST)
    other_user = User.objects.get(username=username)
    if form.is_valid():
        work_record = form.save(commit=False)
        work_record.user = other_user
        work_record.save()
        return HttpResponseRedirect(reverse('profile_detail', kwargs={'username': other_user.username }))

    else:
        return render_to_response(
                'profiles/new_work_record.html',
                {
                'form': form,
                'other_user': other_user,
                },
                context_instance=RequestContext(request)
                )

@owner_required(MemberProfile)
def new_work_record(request, username, template_name='profiles/new_work_record.html', object=None):
    # Handle POST to new as a create request
    if request.method == 'POST':
        return work_records_index(request, username)
    other_user = get_object_or_404(User, username=username)
    form = WorkRecordForm()
    return render_to_response(
            template_name,
            {
            'form': form,
            'other_user': other_user,
            },
            context_instance=RequestContext(request)
            )

def work_record_detail(request, username, work_record_id, template_name='profiles/work_record_detail.html'):
    if request.method == 'POST':
        return update_work_record(request, username=username, work_record_id=work_record_id)
    other_user = get_object_or_404(User, username=username)
    work_record = get_object_or_404(WorkRecord, id=work_record_id)
    return render_to_response(
            template_name,
            {
                'work_record': work_record,
                'other_user': other_user,
            },
            context_instance=RequestContext(request)
            )
    return get_work_record(request, **kwargs)

@owner_required(WorkRecord)
def update_work_record(request, username, work_record_id, object=None):
    if object:
        work_record = object
    else:
        work_record = get_object_or_404(WorkRecord, id=work_record_id)
    form = WorkRecordForm(request.POST, instance=work_record)
    other_user = User.objects.get(username=username)

    # if form saves, redirect to profile_detail
    if form.is_valid():
        work_record = form.save(commit=False)
        work_record.user = other_user
        work_record.save()
        return HttpResponseRedirect(reverse('profile_detail', kwargs={'username': other_user.username }))
        # if save fails, go back to edit_resource page
    else:
        return render_to_response(
                'profiles/edit_work_record.html',
                {
                    'form': form,
                    'work_record': work_record,
                    'other_user': other_user,
                },
                context_instance=RequestContext(request)
                )


@owner_required(WorkRecord)
def edit_work_record(request, username, work_record_id, template_name='profiles/edit_work_record.html', object=None):
    if request.method == 'POST':
        return update_work_record(request, username=username, work_record_id=work_record_id, object=object)
    other_user = get_object_or_404(User, username=username)
    if object:
        work_record = object
    else:
        work_record = get_object_or_404(WorkRecord, id=work_record_id)
    form = WorkRecordForm(instance=work_record)
    return render_to_response(
            template_name,
            {
                'form': form,
                'work_record': work_record,
                'other_user': other_user,
            },
            context_instance=RequestContext(request)
            )

@owner_required(WorkRecord)
def delete_work_record(request, username, work_record_id, object=None):
    if object:
        work_record = object
    else:
        work_record = get_object_or_404(WorkRecord, id=work_record_id)
    if request.method == 'POST':
        work_record.delete()
        return HttpResponseRedirect(reverse('work_record_index', kwargs={'username': username}))
    
def search_profile(request, username):
	profiles = []
	term = ""
	
	if request.method == 'POST':
		form = ProfileSearchForm(request.POST)

		if form.is_valid():
			term = form.cleaned_data['searchterm']
			profiles = MemberProfile.objects.filter(
							name__icontains=form.cleaned_data['searchterm']) | \
                            MemberProfile.objects.filter(
                            user__username__icontains=form.cleaned_data['searchterm'])
			
#		profiles = MemberProfile.objects.all()
		
	return render_to_response("profiles/searchresult.html", {
		"profiles": profiles,
		"term": term,
    }, context_instance=RequestContext(request))

