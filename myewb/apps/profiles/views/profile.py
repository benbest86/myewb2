"""myEWB profile views
Functions used to display additional (or replacement) profile-related views not provided by Pinax's profiles app.

This file is part of myEWB
Copyright 2009-2010 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2009-06-22
Last modified: 2010-01-04
@author: Joshua Gorner, Francis Kung, Ben Best
"""

import random, sha
from datetime import date, timedelta
from django.shortcuts import get_object_or_404
from pinax.apps.profiles.views import *
from pinax.apps.profiles.views import profile as pinaxprofile
from django.template import RequestContext, Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from siteutils import online_middleware
from siteutils.helpers import get_email_user
from siteutils.decorators import owner_required, secure_required
from siteutils.models import PhoneNumber
from siteutils.context_processors import timezones
from profiles.models import MemberProfile, StudentRecord, WorkRecord, ToolbarState
from profiles.forms import StudentRecordForm, WorkRecordForm, MembershipForm, MembershipFormPreview, PhoneNumberForm, SettingsForm 

from networks.models import Network
from networks.helpers import is_exec_over
from base_groups.models import GroupMember
from base_groups.forms import GroupBulkImportForm
from creditcard.forms import PaymentForm
from creditcard.models import Payment, Product
from friends_app.forms import InviteFriendForm

@login_required
def profiles(request, template_name="profiles/profiles.html"):
    search_terms = request.GET.get('search', '')
    if search_terms:
        # allow space-deliminated search terms
        qry = Q(profile__name__icontains=search_terms.split()[0])
        for term in search_terms.split()[1:]:
            qry = qry & Q(profile__name__icontains=term)
            
        # normal users just get that, and nothing else...
        if not request.user.has_module_perms("profiles"):
            users = User.objects.filter(is_active=True).filter(qry)
            users = users.filter(memberprofile__grandfathered=False)
            
        # people with profile super-permissions get more results
        else:
            # include email addresses in search
            qry2 = Q(emailaddress__email__icontains=search_terms.split()[0])
            for term in search_terms.split()[1:]:
                qry2 = qry2 & Q(emailaddress__email__icontains=term)
            qry = qry | qry2
            
            # also include usernames... why not...
            qry2 = Q(username__icontains=search_terms.split()[0])
            for term in search_terms.split()[1:]:
                qry2 = qry2 & Q(username__icontains=term)
            qry = qry | qry2
            
            users = User.objects.filter(is_active=True).filter(qry)
            
        users = users.distinct().order_by("profile__name")
    else:
        users = None
    
    return render_to_response(template_name, {
        "users": users,
        'search_terms': search_terms,
    }, context_instance=RequestContext(request))
    
@login_required
def profile_edit(request, form_class=ProfileForm, **kwargs):

    template_name = kwargs.get("template_name", "profiles/profile_edit.html")

    if request.is_ajax():
        template_name = kwargs.get(
            "template_name_facebox",
            "profiles/profile_edit_facebox.html"
        )

    other_user = request.user
    profile = request.user.get_profile()

    if request.method == "POST":
        if request.POST.get("formtype") == "phone":
            profile_form = form_class(instance=profile)
            phone_form = PhoneNumberForm(request.POST)
            
            if phone_form.is_valid():
                phone = phone_form.save(commit=False)
                phone.content_object = profile
                phone.save()
                
                phone_form = PhoneNumberForm()
                
        elif request.POST.get("formtype") == "phonedelete":
            phone = get_object_or_404(PhoneNumber, pk=request.POST.get("phoneid"))
            
            if phone in profile.phone_numbers.all():
                phone.delete()
            else:
                return HttpResponseForbidden()
            
            phone_form = PhoneNumberForm()
            profile_form = form_class(instance=profile)
        else:
            profile_form = form_class(request.POST, instance=profile)
            phone_form = PhoneNumberForm()
            if profile_form.is_valid():
                profile = profile_form.save(commit=False)
                profile.user = request.user
                profile.save()
                return HttpResponseRedirect(reverse("profile_detail", args=[request.user.username]))
    else:
        profile_form = form_class(instance=profile)
        phone_form = PhoneNumberForm()

    return render_to_response(template_name, {
        "profile": profile,
        "other_user": other_user,
        "profile_form": profile_form,
        "phone_form": phone_form
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
        
        """
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
        """
        
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
        
        """
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
        """
        
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

def profile_by_id(request, profile_id):
    try:
        user = User.objects.get(id=profile_id)
        return HttpResponseRedirect(reverse('profile_detail', kwargs={'username': user.username}))
    except:
        return profile(request, profile_id)

# override default "save" function so we can prompt people to join networks
def profile(request, username, template_name="profiles/profile.html", extra_context=None):
    other_user = get_object_or_404(User, username=username)

    if not other_user.is_active:
        return render_to_response('profiles/deleted.html', {}, context_instance=RequestContext(request)) 

    """
    This is really really neat code, but dunno where to put it since 
    address is now handled via ajax widget...!!
    
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
    """
    
    if extra_context == None:
        extra_context = {}
        
    profile = other_user.get_profile()
    if profile.membership_expiry != None and profile.membership_expiry > date.today():
        extra_context['regular'] = True
    if profile.membership_expiry == None or \
        profile.membership_expiry < date.today() + timedelta(30):
        extra_context['renew'] = True  

#    if template_name == None:
#        return pinaxprofile(request, username, extra_context=extra_context)
#    else:
#        return pinaxprofile(request, username, template_name, extra_context)
    if extra_context is None:
        extra_context = {}
    
    other_user = get_object_or_404(User, username=username)
    
    if request.user.is_authenticated():
        is_friend = Friendship.objects.are_friends(request.user, other_user)
        
        if is_friend:
            invite_form = None
            previous_invitations_to = None
            previous_invitations_from = None
            if request.method == "POST":
                if request.POST.get("action") == "remove": # @@@ perhaps the form should just post to friends and be redirected here
                    Friendship.objects.remove(request.user, other_user)
                    request.user.message_set.create(message=_("You have removed %(from_user)s from friends") % {'from_user': other_user.visible_name()})
                    is_friend = False
                    invite_form = InviteFriendForm(request.user, {
                        'to_user': username,
                        'message': ugettext("Let's be friends!"),
                    })
        
        else:
            if request.user.is_authenticated() and request.method == "POST":
                if request.POST.get("action") == "invite": # @@@ perhaps the form should just post to friends and be redirected here
                    invite_form = InviteFriendForm(request.user, request.POST)
                    if invite_form.is_valid():
                        invite_form.save()
                else:
                    invite_form = InviteFriendForm(request.user, {
                        'to_user': username,
                        'message': ugettext("Let's be friends!"),
                    })
                    invitation_id = request.POST.get("invitation", None)
                    if request.POST.get("action") == "accept": # @@@ perhaps the form should just post to friends and be redirected here
                        try:
                            invitation = FriendshipInvitation.objects.get(id=invitation_id)
                            if invitation.to_user == request.user:
                                try:                                # have gotten IntegrityError from this... #573
                                    invitation.accept()             # (accepting an already-accepted invite, maybe?)
                                except:
                                    pass
                                request.user.message_set.create(message=_("You have accepted the friendship request from %(from_user)s") % {'from_user': invitation.from_user.visible_name()})
                        except FriendshipInvitation.DoesNotExist:
                            pass
                    elif request.POST.get("action") == "decline": # @@@ perhaps the form should just post to friends and be redirected here
                        try:
                            invitation = FriendshipInvitation.objects.get(id=invitation_id)
                            if invitation.to_user == request.user:
                                invitation.decline()
                                request.user.message_set.create(message=_("You have declined the friendship request from %(from_user)s") % {'from_user': invitation.from_user.visible_name()})
                        except FriendshipInvitation.DoesNotExist:
                            pass
            else:
                invite_form = InviteFriendForm(request.user, {
                    'to_user': username,
                    'message': ugettext("Let's be friends!"),
                })
        
            is_friend = Friendship.objects.are_friends(request.user, other_user)

        #is_following = Following.objects.is_following(request.user, other_user)
        #other_friends = Friendship.objects.friends_for_user(other_user)
        
        friends_qry = Friendship.objects.filter(Q(from_user=other_user) | Q(to_user=other_user))\
                                        .select_related(depth=1).order_by('?')[:10]
        other_friends = []
        for f in friends_qry:
            if f.to_user == other_user:
                other_friends.append(f.from_user)
            else:
                other_friends.append(f.to_user)
        
        if request.user == other_user:
            is_me = True
        else:
            is_me = False
            
        pending_requests = FriendshipInvitation.objects.filter(to_user=other_user, status=2).count()
        previous_invitations_to = FriendshipInvitation.objects.invitations(to_user=other_user, from_user=request.user)
        previous_invitations_from = FriendshipInvitation.objects.invitations(to_user=request.user, from_user=other_user)
        
        # friends & admins have visibility.
        has_visibility = is_friend or request.user.has_module_perms("profiles")
        if not has_visibility:      #but so does your chapter's exec
            mygrps = Network.objects.filter(members__user=request.user, members__is_admin=True, is_active=True).order_by('name')
            if len(list(set(mygrps) & set(other_user.get_networks()))) > 0:
                has_visibility = True
        
    else:
        other_friends = []
        is_friend = False
        is_me = False
        is_following = False
        pending_requests = 0
        invite_form = None
        previous_invitations_to = None
        previous_invitations_from = None
        has_visibility = False
    
    return render_to_response(template_name, dict({
        "is_me": is_me,
        "is_friend": is_friend,
        #"is_following": is_following,
        "is_exec_over": is_exec_over(other_user, request.user), 
        "other_user": other_user,
        "other_friends": other_friends,
        "invite_form": invite_form,
        "previous_invitations_to": previous_invitations_to,
        "previous_invitations_from": previous_invitations_from,
        "pending_requests": pending_requests,
        "has_visibility": has_visibility,
    }, **extra_context), context_instance=RequestContext(request))

@secure_required
def pay_membership(request, username):
    other_user = User.objects.get(username=username)
    
    # Show payment form if you are upgrading yourself
    if request.user == other_user:
        chapters = Network.objects.filter(chapter_info__isnull=False,
                                          member_users=request.user,
                                          is_active=True)
        form = MembershipForm(chapters=chapters)
        form.helper.action = reverse('profile_pay_membership2', kwargs={'username': username})
    
        return render_to_response(
            'creditcard/new_payment.html',
            {'form': form},
            context_instance=RequestContext(request)
            )
         
    # Admins / chapter execs can upgrade anyone's membership
    elif request.user.has_module_perms("profiles") or is_exec_over(other_user, request.user):
        other_user.get_profile().pay_membership()
        message = loader.get_template("profiles/member_upgraded.html")
        c = Context({'user': other_user.visible_name()})
        request.user.message_set.create(message=message.render(c))
        return HttpResponseRedirect(reverse('profile_detail', kwargs={'username': username }))
    
    # should not happen.. duh duh duh!
    else:
        return render_to_response('denied.html', context_instance=RequestContext(request))
    
@secure_required
def pay_membership2(request, username):
    other_user = User.objects.get(username=username)
    
    # Show payment form if you are upgrading yourself
    if request.user == other_user:
        if request.method == 'POST':
            chapters = Network.objects.filter(chapter_info__isnull=False,
                                              member_users=request.user,
                                              is_active=True)
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
                form.user = other_user
                form.helper.action = reverse('profile_pay_preview', kwargs={'username': username})

                return render_to_response(
                                          'creditcard/new_payment.html',
                                          {'form': form},
                                           context_instance=RequestContext(request)
                                           )
            else:    
                f.helper.action = reverse('profile_pay_membership2', kwargs={'username': username})
            
                return render_to_response(
                    'creditcard/new_payment.html',
                    {'form': f},
                    context_instance=RequestContext(request)
                    )
                
        # what kind of error to throw...?
         
    # Admins / chapter execs can upgrade anyone's membership
    elif request.user.has_module_perms("profiles") or is_exec_over(other_user, request.user):
        other_user.get_profile().pay_membership()
        message = loader.get_template("profiles/member_upgraded.html")
        c = Context({'user': other_user.visible_name()})
        request.user.message_set.create(message=message.render(c))
        return HttpResponseRedirect(reverse('profile_detail', kwargs={'username': username }))
    
    # should not happen.. duh duh duh!
    else:
        return render_to_response('denied.html', context_instance=RequestContext(request))

@secure_required
def pay_membership_preview(request, username):        
    return MembershipFormPreview(PaymentForm)(request, username=username)
        
@staff_member_required   
def impersonate (request, username):
    user = get_object_or_404(User, username=username)
    
    if user.get_profile().grandfathered:
        request.user.message_set.create(message="%s has not logged into the new myewb yet; you can't impersonate them." % user.visible_name())
        
    else:
        logout(request)
        online_middleware.remove_user(request)
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)
    
        request.user.message_set.create(message="Welcome, %s impersonator!" % user.visible_name())

    return HttpResponseRedirect(reverse('home'))

# is there a decorator that uses user.has_module_perms instead of user.has_perms ?
@permission_required('profiles.admin')
def mass_delete(request):
    if request.method == 'POST':
        # re-use GroupBulkImportForm because it does all we need
        # (TODO: genericize that =) )
        form = GroupBulkImportForm(request.POST)
        if form.is_valid():
            raw_emails = form.cleaned_data['emails']
            emails = raw_emails.split()   # splits by whitespace characters
            success = 0
            
            for email in emails:
                email_user = get_email_user(email)
                if email_user is not None and email_user.is_bulk:
                    email_user.softdelete()
                    success += 1
                
            request.user.message_set.create(message="Deleted %d of %d" % (success, len(emails)))
            return HttpResponseRedirect(reverse('home'))
    else:
        form = GroupBulkImportForm()
    return render_to_response("profiles/mass_delete.html", {
        "form": form,
    }, context_instance=RequestContext(request))
    
def softdelete(request, username):
    user = get_object_or_404(User, username=username)

    if request.user == user or request.user.has_module_perms("profiles"):
        if request.method == 'POST':
            logout(request)
            online_middleware.remove_user(request)
            user.softdelete()
        
            return HttpResponseRedirect(reverse('home'))
        else:
            return render_to_response("profiles/delete_confirm.html", {
                "other_user": user,
            }, context_instance=RequestContext(request))
    else:
        return HttpResponseForbidden()

@login_required
def settings(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    if request.user == user or request.user.has_module_perms("profiles"):
        if request.method == 'POST':
            form = SettingsForm(request.POST,
                                instance=user.get_profile())
            
            if form.is_valid():
                form.save()
            
                request.user.message_set.create(message='Settings updated.')
                return HttpResponseRedirect(reverse('profile_detail', kwargs={'username': user.username}))
            
        else:
            form = SettingsForm(instance=user.get_profile())
        
            return render_to_response("profiles/edit_settings.html",
                                      {"other_user": user,
                                       "form": form,
                                       'is_me': user.pk == request.user.pk},
                                       context_instance=RequestContext(request))
    else:
        return HttpResponseForbidden()

@login_required
def toolbar_action(request, action=None, toolbar_id=None):
    if action == None or toolbar_id == None:
        return HttpResponseForbidden
    
    try:
        state, created = ToolbarState.objects.get_or_create(user=request.user,
                                                            toolbar=toolbar_id)
    # i guess this happens very rarely as a race condition???
    except ToolbarState.MultipleObjectsReturned:
        states = ToolbarState.objects.filter(user=request.user,
                                             toolbar=toolbar_id)
        state = states[0]
        for s in states[1:]:
            s.delete()
        
    if action == "close":
        state.state = "c"
    else:
        state.state = "o"
    state.save()
    
    return HttpResponse("")

def timezone_switch(request):
    if request.method == 'POST':
        timezone = request.POST.get('timezone', None)
        redirect = request.POST.get('redirect', None)
        
        if timezone and redirect and (timezone in timezones or timezone == "auto"):
            if timezone == "auto":
                timezone = None
            
            if request.user.is_authenticated() and False:
                profile = request.user.get_profile()
                profile.timezone = timezone
                profile.save() 
            else:
                request.session['timezone'] = timezone
                
            return HttpResponseRedirect(redirect)
    
    return HttpResponseForbidden
