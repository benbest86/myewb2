"""myEWB user search

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors
"""

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from forms import UserSearchForm, SampleUserSearchForm, SampleMultiUserSearchForm

from networks.models import Network
from base_groups.models import BaseGroup

def user_search(request):
    field = request.POST.get('usi_field', '')
    first_name = request.POST.get('usi_first_name', None)
    last_name = request.POST.get('usi_last_name', None)
    #chapter = request.POST.get('chapter', None)
    #chapters = Network.objects.filter(chapter_info__isnull=False)
    
    if first_name or last_name:
        if first_name and last_name:
            qry = Q(first_name__icontains=first_name) & Q(last_name__icontains=last_name)
        elif first_name:
            qry = Q(first_name__icontains=first_name)
        elif last_name:
            qry = Q(last_name__icontains=last_name)
            
        #if chapter and not chapter == 'none':
        #    qry = qry & Q(member_groups__group__slug=chapter)
        if not request.user.has_module_perms("profiles"):
            # don't show grandfathered users
            # (this is a huge performance hit, as it adds an outer join... =( )
            # (removed 06/30/10 - no privacy concern here, I think.  this is different
            #  than a general profile search...)
            #qry = qry & Q(memberprofile__grandfathered=False)
            
            # restrict results to friends or people in your chapter, too
            mygrps = BaseGroup.objects.filter(member_users=request.user, is_active=True).exclude(model="LogisticalGroup")
            qry = qry & (Q(member_groups__group__in=mygrps) | Q(friends=request.user) | Q(_unused_=request.user))

        # build the final query
        qry = qry & Q(is_active=True)
        users = User.objects.filter(qry).order_by('first_name', 'last_name')
        usercount = users.count()
    else:
        users = None
        usercount = 0
        
    if request.is_ajax():
        return render_to_response(
                'user_search/user_search_ajax_results.html', 
                {
                    'users': users,
                    'toomany': (usercount > 50),
                    'field': field
                }, context_instance=RequestContext(request))
    
def sample_user_search(request):
    form = SampleUserSearchForm(request.POST)
    
    if request.method == 'POST':
        if form.is_valid():

            to_user = form.cleaned_data['to']
            cc_user = form.cleaned_data['cc']
            bcc_user = form.cleaned_data['bcc']
        
            return render_to_response(
                    'user_search/sample_user_search.html', 
                    { 
                        'form': form,
                        'results': True,
                        'to_user': to_user,
                        'cc_user': cc_user,
                        'bcc_user': bcc_user
                    }, 
                    context_instance=RequestContext(request))
    return render_to_response(
            'user_search/sample_user_search.html', 
            { 
                'form': form
            }, 
            context_instance=RequestContext(request))
            
def sample_multi_user_search(request):
    form = SampleMultiUserSearchForm(request.POST)
    
    if request.method == 'POST':
        if form.is_valid():
            to_users = form.cleaned_data['to']
            cc_users = form.cleaned_data['cc']
            bcc_users = form.cleaned_data['bcc']
            
            return render_to_response(
                    'user_search/sample_multi_user_search.html', 
                    { 
                        'form': form,
                        'results': True,
                        'to_users': to_users,
                        'cc_users': cc_users,
                        'bcc_users': bcc_users
                    }, 
                    context_instance=RequestContext(request))
    return render_to_response(
            'user_search/sample_multi_user_search.html', 
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
                'user_search/selected_user.html', 
                {
                    'sel_user': sel_user,
                    'field': field
                }, context_instance=RequestContext(request))

def autocomplete(request, app, model):
    model_class = ContentType.objects.get(app_label=app, model=model).model_class()
    if request.GET.get('q', None):
        list = model_class.objects.filter(name__icontains=request.GET['q'])[:30]
        results = ""
        for l in list:
            results = results + l.name + "\n" 
        return HttpResponse(results)
    
    return HttpResponse('')
