"""myEWB user search

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
"""

from django.shortcuts import get_object_or_404
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from forms import UserSearchForm, SampleUserSearchForm

from networks.models import Network
from base_groups.models import GroupMember

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
    
def sample_user_search(request):
    form = SampleUserSearchForm(request.POST)
    
    if request.method == 'POST':
        if form.is_valid():

            to_users = form.cleaned_data['to']
            cc_users = form.cleaned_data['cc']
            bcc_users = form.cleaned_data['bcc']
        
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
