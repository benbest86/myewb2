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
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import simplejson

from siteutils.models import Address
from profiles.forms import AddressForm

def get_address_or_404(user, label):
    profile = user.get_profile()
    content_type = ContentType.objects.get_for_model(profile)
    return get_object_or_404(Address, content_type__pk=content_type.id, object_id=profile.id, label=label)

def address_index(request, username):
    # if request.is_ajax():
    if request.method == 'GET':
        other_user = get_object_or_404(User, username=username)
        profile = other_user.get_profile()
        content_type = ContentType.objects.get_for_model(user)
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

def create_address(request, username):
    form = AddressForm(request.POST)
    if form.is_valid():
        address = form.save(commit=False)
        other_user = get_object_or_404(User, username=username)
        profile = other_user.get_profile()
        address.content_object = profile
        address.save()
        if request.is_ajax():
            return HttpResponse(simplejson.dumps({'created': True, 'label': address.label}), mimetype='application/javascript')
        else:
            return HttpResponseRedirect(reverse('profile_address_detail', kwargs={'username': username, 'label': address.label}))
    else:
        if request.is_ajax():
            error_data = {
                'created': False,
                'label': address.label,
                'rendered_form': render_to_response(
                                    'profiles/new_address.html', 
                                    {
                                        'other_user': other_user, 
                                        'form': form, 
                                        },
                                    )
            }
            return HttpResponse(simplejson.dumps(error_data), mimetype='application/javascript')            
        else:
            return render_to_response(
                    'profiles/new_address.html',
                    {
                        'other_user': other_user,
                        'form': form,
                        },
                    )

def new_address(request, username):
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

def address_detail(request, username, label):
    # if request.is_ajax():
    other_user = get_object_or_404(User, username=username)
    address = get_address_or_404(other_user, label)
    # retrieve details
    if request.method == 'GET':
        return render_to_response(
                'profiles/address_detail.html',
                {
                    'other_user': other_user,
                    'address': address,
                    },
                )
        # update existing resource
    elif request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        # if form saves, return detail for saved resource
        if form.is_valid():            
            address = form.save()
            if request.is_ajax():
                return HttpResponse(simplejson.dumps({'valid': True, 'label': address.label}), mimetype='application/javascript')
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
                error_data = {
                    'valid': False,
                    'label': address.label,
                    'rendered_form': render_to_response(
                                        'profiles/edit_address.html',
                                        {
                                            'form': form,
                                            'other_user': other_user,
                                            'address': address,
                                            },
                                        )
                }
                return HttpResponse(simplejson.dumps(error_data), mimetype='application/javascript')
            else:
                return render_to_response(
                        'profiles/edit_address.html',
                        {
                            'form': form,
                            'other_user': other_user,
                            'address': address,
                            },
                        )

def edit_address(request, username, label):
    # if request.is_ajax():
    if request.method == 'POST':
        return address_detail(request, address_id)
    other_user = get_object_or_404(User, username=username)
    address = get_address_or_404(other_user, label)
    form = AddressForm(instance=address)
    return render_to_response(
            'profiles/edit_address.html',
            {
                'form': form,
                'other_user': other_user,
                'address': address,
                },
            )

def delete_address(request, username, address_id):
    # if request.is_ajax():
    other_user = get_object_or_404(User, username=username)
    address = get_address_or_404(other_user, label)
    if request.method == 'POST':
        address.delete()
        return HttpResponseRedirect(reverse('profiles_address_index'))      # possibly not what we want to do here...
    
