"""myEWB group workspaces

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

Last modified on 2010-08-18
@author Francis Kung
"""

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from base_groups.models import BaseGroup
from base_groups.forms import WorkspaceUploadForm
from base_groups.helpers import group_search_filter, get_counts, get_recent_counts, enforce_visibility 
from base_groups.decorators import group_admin_required, visibility_required

import settings, os

@group_admin_required()
def browse(request, group_slug):
    """
    Browse a group's workspace
    """
    group = get_object_or_404(BaseGroup, slug=group_slug)
    
    response = []
    if request.method == 'POST':
        # create folder for the group's workspace if needed
        dir = os.path.join(settings.MEDIA_ROOT, 'workspace', 'groups', group_slug)
        if not os.path.isdir(dir):
            os.mkdir(dir, 0755)
        
        # find the requested directory, performing some security checks
        requestdir = request.POST.get('dir', '/')
        if requestdir.find('.') > -1:       # do not allow any periods
            return HttpResponse('')

        # build directory listing
        dir = dir + requestdir
        if os.path.isdir(dir):
            response = ['<ul class="jqueryFileTree" style="display: none;">']
            
            # take all files/subdirectories and build lists
            files = []
            dirs = []
            for f in os.listdir(dir):
                if os.path.isdir(os.path.join(dir, f)):
                    dirs.append(f)
                else:
                    files.append(f)
                    
            # sort lists
            dirs.sort()
            files.sort()
                
            # output directories...
            for f in dirs:
                full_file = os.path.join(requestdir, f)
                response.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' % (full_file, f))
                
            # output files
            for f in files:
                full_file = os.path.join(requestdir, f)
                fname, ext = os.path.splitext(f)
                ext = ext[1:]
                response.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (ext, full_file, f))
    
            response.append('</ul>')
        
    # return listing
    return HttpResponse(''.join(response))

@group_admin_required()
def detail(request, group_slug):
    """
    View the details of a file
    """
    group = get_object_or_404(BaseGroup, slug=group_slug)
    
    response = []
    if request.method == 'POST' and request.POST.get('dir', None):
        return detail_display(request, group, request.POST['dir'])
    
    else:
        return HttpResponse("error")
    
def detail_display(request, group, requestdir):
    # the group's workspace root
    dir = os.path.join(settings.MEDIA_ROOT, 'workspace', 'groups', group.slug)

    # build the specific file
    requestfile, ext = os.path.splitext(requestdir)
    if requestfile.find('.') > -1:       # do not allow any periods in the path
        return HttpResponse('invalid file requested')
    f = dir + requestdir
    
    if os.path.isfile(f):
        # retrieve misc info
        path, filename = os.path.split(requestdir[1:])
        stat = os.stat(f)
        return render_to_response("base_groups/workspace/detail.html",
                                  {'path': path,
                                   'filename': filename,
                                   'relpath': requestdir,
                                   'stat': stat,
                                   'group': group},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponse("cannot find file")

@group_admin_required()
def upload(request, group_slug):
    """
    Upload a new file
    """
    group = get_object_or_404(BaseGroup, slug=group_slug)
    
    if request.method == 'POST':
        form = WorkspaceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # find absolute directory
            dir = os.path.join(settings.MEDIA_ROOT, 'workspace', 'groups', group.slug)
            filename = request.FILES['file'].name

            # open file
            file = open(dir + '/' + filename, 'wb+')
            
            # write file to disk
            for chunk in request.FILES['file'].chunks():
                file.write(chunk)
            file.close() 
            
            # redirect to file info display
            return detail_display(request, group, '/' + filename)
    else:
        form = WorkspaceUploadForm()
        
    return render_to_response("base_groups/workspace/upload.html",
                              {'form': form,
                               'group': group},
                               context_instance=RequestContext(request))

@group_admin_required()
def move(request, group_slug):
    """
    View the details of a file
    """
    group = get_object_or_404(BaseGroup, slug=group_slug)
    return HttpResponse("not implemente")

@group_admin_required()
def replace(request, group_slug):
    """
    View the details of a file
    """
    group = get_object_or_404(BaseGroup, slug=group_slug)
    return HttpResponse("not implemente")

@group_admin_required()
def delete(request, group_slug):
    """
    View the details of a file
    """
    group = get_object_or_404(BaseGroup, slug=group_slug)
    return HttpResponse("not implemente")
