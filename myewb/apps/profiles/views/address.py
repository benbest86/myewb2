"""myEWB profile views - address

This file is part of myEWB
Copyright 2009-2010 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2010-01-04
Last modified: 2010-01-04
@author: Joshua Gorner (parts derived from code by Ben Best)
"""

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context, loader
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import simplejson

from friends.models import Friendship
from siteutils.models import Address
from profiles.forms import AddressForm
from profiles.models import MemberProfile
from siteutils.http import JsonResponse
from siteutils.decorators import owner_required
from siteutils.shortcuts import get_object_or_none

def is_label_unique_for_user(user, label, instance=None):
    profile = user.get_profile()
    content_type = ContentType.objects.get_for_model(profile)
    existing_list = Address.objects.filter(content_type__pk=content_type.id, object_id=profile.id, label=label)
    if existing_list.count() == 0 or existing_list[0] == instance:
        return True
    else:
        return False

def get_address_or_404(user, label):
    profile = user.get_profile()
    content_type = ContentType.objects.get_for_model(profile)
    
    address = get_object_or_none(Address, content_type__pk=content_type.id, object_id=profile.id, label=label)
    if not address:
        address = get_object_or_none(Address, content_type__pk=content_type.id, object_id=profile.id, id=label)
    
    # TODO: if address is None: return 404
    return address

# Not really used at the moment
@owner_required(MemberProfile)
def address_index(request, username, object=None):
    # if request.is_ajax():
    if request.method == 'GET':
        other_user = get_object_or_404(User, username=username)
        profile = other_user.get_profile()
        content_type = ContentType.objects.get_for_model(other_user)
        addresses = Address.objects.filter(content_type=content_type, object_id=profile.id)
        return render_to_response(
                'profiles/address_index.html',
                {
                    'other_user': other_user,
                    'addresses': addresses,
                    },
                )
    elif request.method == 'POST':
        return create_address(request, username)

@owner_required(MemberProfile)
def create_address(request, username, object=None):
    form = AddressForm(request.POST)
    other_user = get_object_or_404(User, username=username)
    if form.is_valid() and is_label_unique_for_user(other_user, form.cleaned_data['label'], None):
        address = form.save(commit=False)
        profile = other_user.get_profile()
        address.content_object = profile
        address.save()
        profile.addresses.add(address)
        if request.is_ajax():
            return JsonResponse({'valid': True, 'label': address.label, 'id': address.pk})
            # return HttpResponse(simplejson.dumps({'valid': True, 'label': address.label}), mimetype='application/javascript')
        else:
            #return HttpResponseRedirect(reverse('profile_address_detail', kwargs={'username': username, 'label': address.label}))
            return HttpResponseRedirect(reverse('profile_edit'))
    else:
        label = ""
        label_error = False
        if form.is_valid():
            label = form.cleaned_data['label']
            label_error = not is_label_unique_for_user(other_user, form.cleaned_data['label'], None)
            
        if request.is_ajax():
            error_html =  render_to_string('profiles/new_address.html',
                                           {'form': form,
                                            'other_user': other_user
                                           })
            error_data = {
                'valid': False,
                'html': error_html
                #'label': label,
                #'errors': errorlist,
                #'label_error': label_error
            }
            return JsonResponse(error_data)
            # return HttpResponse(simplejson.dumps(error_data), mimetype='application/javascript')            
        else:
            return render_to_response(
                    'profiles/new_address.html',
                    {
                        'other_user': other_user,
                        'form': form,
                        },
                    )

@owner_required(MemberProfile)
def new_address(request, username, object=None):
    # if request.is_ajax():
    other_user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        return create_address(request, username)
    form = AddressForm()
    return render_to_response(
            'profiles/new_address.html',
            {
                'other_user': other_user,
                'form': form,
                },
            )

def address_detail(request, username, id):
    # if request.is_ajax():
    other_user = get_object_or_404(User, username=username)
    address = get_address_or_404(other_user, id)
    
    is_friend = Friendship.objects.are_friends(request.user, other_user)
    is_me = (other_user == request.user)
    # retrieve details
    if request.method == 'GET' and (is_friend or is_me):
        return render_to_response(
                'profiles/address_detail.html',
                {
                    'other_user': other_user,
                    'address': address,
                    'is_me': is_me
                    },
                )
        # update existing resource
    elif request.method == 'POST' and is_me:
        form = AddressForm(request.POST, instance=address)
        
        # if form saves, return detail for saved resource
        if form.is_valid() and is_label_unique_for_user(other_user, form.cleaned_data['label'], address):
            address = form.save()
            if request.is_ajax():
                return JsonResponse({'valid': True, 'label': address.label, 'id': address.pk})
                # return HttpResponse(simplejson.dumps(), mimetype='application/javascript')
            else:
                return render_to_response(
                        'profiles/address_detail.html',
                        {
                            'other_user': other_user,
                            'address': address,
                            },
                        )
            # if save fails, go back to edit_resource page
        else:
            if request.is_ajax():
                error_html =  render_to_string('profiles/edit_address.html',
                                               {'form': form,
                                                'other_user': other_user,
                                                'address': address,
                                               })
                error_data = {
                    'valid': False,
                    'html': error_html,
                    #'label': address.label,
                    #'errors': form.errors,
                    #'label_error': not is_label_unique_for_user(other_user, form.POST.get('label', ''), address)
                }
                return JsonResponse(error_data)
                #return HttpResponse(simplejson.dumps(error_data), mimetype='application/javascript')
            else:
                return render_to_response(
                        'profiles/edit_address.html',
                        {
                            'form': form,
                            'other_user': other_user,
                            'address': address,
                            },
                        )

@owner_required(MemberProfile)
def edit_address(request, username, id, object=None):
    # if request.is_ajax():
    if request.method == 'POST':
        return address_detail(request, username, id)
    other_user = get_object_or_404(User, username=username)
    address = get_address_or_404(other_user, id)
    form = AddressForm(instance=address)
    return render_to_response(
            'profiles/edit_address.html',
            {
                'form': form,
                'other_user': other_user,
                'address': address,
                },
            )

@owner_required(MemberProfile)
def delete_address(request, username, id, object=None):
    other_user = get_object_or_404(User, username=username)
    address = get_address_or_404(other_user, id)
    if request.method == 'POST':
        address.delete()
        if request.is_ajax():
            return JsonResponse({'valid': True, 'deleted': True})
        else:
            return HttpResponseRedirect(reverse('profiles_address_index'))      # possibly not what we want to do here...
