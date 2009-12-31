"""myEWB profile views
Functions used to display additional (or replacement) profile-related views not provided by Pinax's profiles app.

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2009-06-22
Last modified: 2009-08-02
@author: Joshua Gorner, Francis Kung, Ben Best
"""

import random, sha
from datetime import date, timedelta
from django.shortcuts import get_object_or_404
from pinax.apps.profiles.views import *
from pinax.apps.profiles.views import profile as pinaxprofile
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from siteutils.decorators import owner_required
from profiles.models import MemberProfile, StudentRecord, WorkRecord
from profiles.forms import StudentRecordForm, WorkRecordForm, MembershipForm, UserSearchForm, SampleUserSearchForm

from networks.models import Network
from base_groups.models import GroupMember
from creditcard.forms import PaymentForm
from creditcard.models import Payment, Product

def profiles(request, template_name="profiles/profiles.html"):
    search_terms = request.GET.get('search', '')
    if search_terms:
        users = User.objects.filter(profile__name__icontains=search_terms) | \
                        User.objects.filter(username__icontains=search_terms)
        users = users.order_by("profile__name")
    else:
        users = User.objects.all().order_by("profile__name")
    
    return render_to_response(template_name, {
        "users": users,        
        'search_terms': search_terms,
    }, context_instance=RequestContext(request))

def student_records_index(request, username, template_name='profiles/student_records_index.html'):
    if request.method == 'POST':
        return create_student_record(request, username)
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
        
        # find network ID (based on name they entered)
        # TODO: remove from network when someone ends their employment
        institution = form.cleaned_data['institution']
        networks = Network.objects.filter(name=institution)
        # networks = networks.filter(network_type='U')
        
        if networks.count() == 0:
            network = Network(network_type='U', slug=institution,
                              name=institution,
                              creator=other_user)
            network.save()
        else:
            network = networks[0]

        # FIXME this should be implemented as a signal - profiles should not know about GroupMember
        existing_members=network.members.filter(user=other_user)
        if existing_members.count() == 0:
            network_member = GroupMember(group=network, user=other_user, is_admin=False)
            network.members.add(network_member)
            network_member.save()

        student_record.network = network
        
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
        return update_student_record(request, username, student_record_id)
    other_user = get_object_or_404(User, username=username)
    student_record = get_object_or_404(StudentRecord, id=student_record_id, user=other_user)
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
    other_user = User.objects.get(username=username)
    if object:
        student_record = object
    else:
        student_record = get_object_or_404(StudentRecord, id=student_record_id, user=other_user)
    form = StudentRecordForm(request.POST, instance=student_record)

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
        student_record = get_object_or_404(StudentRecord, id=student_record_id, user=other_user)
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
        
        employer = form.cleaned_data['employer']
        # find network ID (based on name they entered)
        # TODO: remove from network when someone ends their employment
        networks = Network.objects.filter(name=employer)
        # networks = networks.filter(network_type='C')
        
        if networks.count() == 0:
            # FIXME: this is duplicated in networks.views.networks_index
            # (refactor to centralize)
            # also kinda dupicated below, create_work_record
            network = Network(network_type='C', slug=employer,
                              name=employer,
                              creator=other_user)
            network.save()
        else:
            network = networks[0]

        # FIXME this should be implemented as a signal - profiles should not know about GroupMember
        existing_members=network.members.filter(user=other_user)
        if existing_members.count() == 0:
            network_member = GroupMember(group=network, user=other_user, is_admin=False)
            network.members.add(network_member)
            network_member.save()

        work_record.network = network
        
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
        return update_work_record(request, username, work_record_id)
    other_user = get_object_or_404(User, username=username)
    work_record = get_object_or_404(WorkRecord, id=work_record_id, user=other_user)
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
    other_user = User.objects.get(username=username)
    if object:
        work_record = object
    else:
        work_record = get_object_or_404(WorkRecord, id=work_record_id, user=other_user)
    form = WorkRecordForm(request.POST, instance=work_record)

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
        return update_work_record(request, username, work_record_id, object=object)
    other_user = get_object_or_404(User, username=username)
    if object:
        work_record = object
    else:
        work_record = get_object_or_404(WorkRecord, id=work_record_id, user=other_user)
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

# override default "save" function so we can prompt people to join networks
def profile(request, username, template_name="profiles/profile.html", extra_context=None):
    other_user = User.objects.get(username=username)
    if request.user == other_user:
        if request.method == "POST":
            if request.POST["action"] == "update":
                profile_form = ProfileForm(request.POST, instance=other_user.get_profile())
                if profile_form.is_valid():
                    
                    # if changed city, prompt to update networks
                    if profile_form.cleaned_data['city'] != other_user.get_profile().city:
                        # join new network
                        # TODO: use geocoding to find closest network(s)
                        try:
                            network = Network.objects.get(name=profile_form.cleaned_data['city'], network_type='R')

                            if not network.user_is_member(other_user):
                                message = loader.get_template("profiles/suggest_network.html")
                                c = Context({'network': network, 'action': 'join'})
                                request.user.message_set.create(message=message.render(c))
                        except Network.DoesNotExist:
                            pass
                            
                        # leave old network
                        try:
                            network = Network.objects.get(name=other_user.get_profile().city, network_type='R')
                            if network.user_is_member(other_user):
                                message = loader.get_template("profiles/suggest_network.html")
                                c = Context({'network': network, 'action': 'leave', 'user': other_user})
                                request.user.message_set.create(message=message.render(c))
                        except Network.DoesNotExist:
                            pass
    
    if extra_context == None:
        extra_context = {}
        
    profile = other_user.get_profile()
    if profile.membership_expiry != None and profile.membership_expiry > date.today():
        extra_context['regular'] = True
    if profile.membership_expiry == None or \
        profile.membership_expiry < date.today() + timedelta(30):
        extra_context['renew'] = True  

    if template_name == None:
        return pinaxprofile(request, username, extra_context=extra_context)
    else:
        return pinaxprofile(request, username, template_name, extra_context)

def pay_membership(request, username):
    other_user = User.objects.get(username=username)
    
    # Show payment form if you are upgrading yourself
    if request.user == other_user:
        chapters = Network.objects.filter(chapter_info__isnull=False,
                                          member_users=request.user)
        form = MembershipForm(chapters=chapters)
        form.helper.action = reverse('profile_pay_membership2', kwargs={'username': username})
    
        return render_to_response(
            'creditcard/new_payment.html',
            {'form': form},
            context_instance=RequestContext(request)
            )
         
    # Admins / chapter execs (TODO) can upgrade anyone's membership
    elif request.user.is_superuser:
        other_user.get_profile().pay_membership()
        message = loader.get_template("profiles/member_upgraded.html")
        c = Context({'user': other_user})
        request.user.message_set.create(message=message.render(c))
        return HttpResponseRedirect(reverse('profile_detail', kwargs={'username': username }))
    
    # should not happen.. duh duh duh!
    else:
        return render_to_response('denied.html', context_instance=RequestContext(request))
    
    
def pay_membership2(request, username):
    other_user = User.objects.get(username=username)
    
    # Show payment form if you are upgrading yourself
    if request.user == other_user:
        if request.method == 'POST':
            chapters = Network.objects.filter(chapter_info__isnull=False,
                                              member_users=request.user)
            f = MembershipForm(request.POST, chapters=chapters)
            
            if f.is_valid():
                # will have to do some sku-building once we have chapters in
                if f.cleaned_data['chapter'] == "none":
                    product = Product.objects.get(sku=f.cleaned_data['membership_type'])
                    created = False
                else:
                    product, created = Product.objects.get_or_create(sku="%s-%s" % (f.cleaned_data['membership_type'],
                                                                                    f.cleaned_data['chapter']))
                if created:
                    # TODO: un-hardcode?  Fix so we don't need to do this dynamically?
                    if f.cleaned_data['membership_type'] == 'studues':
                        product.amount = "20.00"
                        product.name = "Student membership (%s)" % f.cleaned_data['chapter']
                        product.save()
                    elif f.cleaned_data['membership_type'] == 'produes':
                        product.amount = "40.00"
                        product.name = "Professional membership (%s)" % f.cleaned_data['chapter']
                        product.save()
                    else:
                        # uhh....!!!
                        pass
                
                form = PaymentForm(initial={'products':product.sku})
                form.helper.action = reverse('profile_pay_preview', kwargs={'username': username})

                return render_to_response(
                                          'creditcard/new_payment.html',
                                          {'form': form},
                                           context_instance=RequestContext(request)
                                           )
                
        # what kind of error to throw...?
         
    # Admins / chapter execs (TODO) can upgrade anyone's membership
    elif request.user.is_superuser:
        other_user.get_profile().pay_membership()
        message = loader.get_template("profiles/member_upgraded.html")
        c = Context({'user': other_user})
        request.user.message_set.create(message=message.render(c))
        return HttpResponseRedirect(reverse('profile_detail', kwargs={'username': username }))
    
    # should not happen.. duh duh duh!
    else:
        return render_to_response('denied.html', context_instance=RequestContext(request))

def user_search(request):
    field = request.POST.get('field', '')
    first_name = request.POST.get('first_name', '')
    last_name = request.POST.get('last_name', '')
    chapter = request.POST.get('chapter', '')
    chapters = Network.objects.filter(chapter_info__isnull=False)
    
    if first_name or last_name or chapter:
        users = User.objects.filter(first_name__icontains=first_name, last_name__icontains=last_name)
        if not chapter == 'none':
            users = users.filter(member_groups__group__slug=chapter)
    else:
        users = None
        
    if request.is_ajax():
        return render_to_response(
                'profiles/user_search_ajax_results.html', 
                {
                    'users': users,
                    'field': field
                }, context_instance=RequestContext(request))
    
def usernames_to_users(usernames):
    users = []
    for username in usernames:
        cur_user = get_object_or_404(User, username=username)
        users.append(cur_user)
    return users

def sample_user_search(request):
    form = SampleUserSearchForm(request.POST)
    
    if request.method == 'POST':
        to_usernames = request.POST.getlist('to')        
        cc_usernames = request.POST.getlist('cc')        
        bcc_usernames = request.POST.getlist('bcc')
        
        to_users = usernames_to_users(to_usernames)
        cc_users = usernames_to_users(cc_usernames)
        bcc_users = usernames_to_users(bcc_usernames)
        
        return render_to_response(
                'profiles/sample_user_search.html', 
                { 
                    'form': form,
                    'results': True,
                    'to_users': to_users,
                    'cc_users': cc_users,
                    'bcc_users': bcc_users
                }, 
                context_instance=RequestContext(request))
    else:
        return render_to_response(
                'profiles/sample_user_search.html', 
                { 
                    'form': form
                }, 
                context_instance=RequestContext(request))
            
def selected_user(request):
    if request.is_ajax() and request.method == 'POST':
        username = request.POST.get('username', '')
        field = request.POST.get('field', '')
        sel_user = User.objects.get(username=username)
        return render_to_response(
                'profiles/selected_user.html', 
                {
                    'sel_user': sel_user,
                    'field': field
                }, context_instance=RequestContext(request))
