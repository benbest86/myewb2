"""myEWB group workspaces

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

Last modified on 2010-08-18
@author Francis Kung
"""

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse

from workspace.decorators import can_view, can_edit
from workspace.models import Workspace
from workspace.forms import WorkspaceUploadForm, WorkspaceMoveForm, WorkspaceNewFolderForm

import settings, os

preview_extensions = ['jpg',
                      'txt',
                      'pdf',
                      'doc',
                      'odt']
preview_aliases = {'jpeg': 'jpg',
                   'gif': 'jpg',
                   'png': 'jpg',
                   'ico': 'jpg',
                   'bmp': 'jpg'}

@can_view()
def browse(request, workspace_id):
    """
    Browse a group's workspace
    """
    workspace = get_object_or_404(Workspace, id=workspace_id)
    
    response = []
    if request.method == 'POST':
        reldir = request.POST.get('dir', '/')
        dir = workspace.get_dir(reldir)
        selected = request.POST.get('selected', '/')[1:].split('/')
        
        # build directory listing
        if dir:
            response = browse_build_tree(dir, reldir, response, selected)
        
    # return listing
    return HttpResponse(''.join(response))

# build dir listing, expanding to the selected element
def browse_build_tree(dir, reldir, response, selected):
    # build initial listing for current directory
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
    
    # find current pre-select element, if any
    if len(selected):
        current = selected.pop(0)
    else:
        current = None
        
    response.append('<ul class="jqueryFileTree" style="display: none;">')
    if len(dirs) or len(files):
        
        # output directories...
        for f in dirs:
            full_file = os.path.join(reldir, f)
            
            if current == f:
                # if this is the pre-selected element, recurse and drill down
                response.append('<li class="directory expanded"><a href="#" rel="%s/">%s</a>' % (full_file, f))
                response = browse_build_tree(os.path.join(dir, f),
                                             reldir + f + '/',
                                             response,
                                             selected)
                response.append('</li>')
            else:
                # otherwise, just a one-line entry
                response.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' % (full_file, f))
            
        # output files
        for f in files:
            full_file = os.path.join(reldir, f)
            fname, ext = os.path.splitext(f)
            ext = ext[1:]
            response.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (ext, full_file, f))

    else:
        if reldir == '/':
            response.append('<li>workspace is empty</li>')
        else:
            response.append('<li>folder is empty</li>')
    response.append('</ul>')
    return response

@can_view()
def detail(request, workspace_id):
    """
    View the details of a file
    """
    workspace = get_object_or_404(Workspace, id=workspace_id)
    
    response = []
    if request.method == 'POST' and request.POST.get('dir', None):
        file = workspace.get_file(request.POST['dir'])
        if file:
            path, filename = os.path.split(request.POST['dir'])
            stat = os.stat(file)
            return render_to_response("workspace/detail.html",
                                      {'workspace': workspace,
                                       'path': path,
                                       'filename': filename,
                                       'relpath': request.POST['dir'],
                                       'stat': stat},
                                      context_instance=RequestContext(request))
    return HttpResponse("error")
    
@can_edit()
def upload(request, workspace_id):
    """
    Upload a new file
    """
    workspace = get_object_or_404(Workspace, id=workspace_id)
    
    # build folder list
    folders = workspace.get_dir_tree()
    
    if request.method == 'POST':
        form = WorkspaceUploadForm(request.POST, request.FILES, folders=folders)
        if form.is_valid():
            # find absolute directory
            dir = workspace.get_dir(form.cleaned_data.get('folder', '/'))
            filename = request.FILES['file'].name
            
            # open file
            file = open(dir + filename, 'wb+')
            
            # write file to disk
            for chunk in request.FILES['file'].chunks():
                file.write(chunk)
            file.close() 
            
            # redirect to file info display
            folder = form.cleaned_data.get('folder', '/')
            if folder == '/':
                folder = ''
            file = dir + filename
            stat = os.stat(file)
            return render_to_response("workspace/detail.html",
                                      {'workspace': workspace,
                                       'path': folder,
                                       'filename': filename,
                                       'relpath': folder + '/' + filename,
                                       'stat': stat,
                                       'force_selection': True},
                                      context_instance=RequestContext(request))
    else:
        form = WorkspaceUploadForm(folders=folders)
        
    return render_to_response("workspace/upload.html",
                              {'form': form,
                               'workspace': workspace},
                               context_instance=RequestContext(request))

@can_edit()
def move(request, workspace_id):
    """
    Move a file
    """
    workspace = get_object_or_404(Workspace, id=workspace_id)
    
    # build folder list
    folders = workspace.get_dir_tree()
    
    if request.method == 'POST':
        form = WorkspaceMoveForm(request.POST, folders=folders)
        if form.is_valid():
            # find absolute directory
            src = workspace.get_file(request.POST.get('file', None))        # src file, full path
            if src:
                leading, file = os.path.split(src)                          # src filename

                folder = workspace.get_dir(form.cleaned_data.get('folder', '/')) # dst folder
                dst = os.path.join(folder, file)                            # dst file, full path
            
            # do the rename!
            if src and folder:
                os.rename(src, dst)
    
                # redirect to file info display
                folder = form.cleaned_data.get('folder', '/')
                if folder == '/':
                    folder = '';
                filepath = folder + file
                stat = os.stat(dst)
                return render_to_response("workspace/detail.html",
                                          {'workspace': workspace,
                                           'path': folder,
                                           'filename': file,
                                           'relpath': folder + '/' + file,
                                           'stat': stat,
                                           'force_selection': True},
                                          context_instance=RequestContext(request))
    else:
        form = WorkspaceMoveForm(folders=folders)
        
    return render_to_response("workspace/move.html",
                              {'form': form,
                               'workspace': workspace},
                               context_instance=RequestContext(request))

@can_edit()
def replace(request, workspace_id):
    """
    View the details of a file
    """
    workspace = get_object_or_404(Workspace, id=workspace_id)
    return HttpResponse("not implemented")

@can_edit()
def delete(request, workspace_id):
    """
    Delete a file
    """
    workspace = get_object_or_404(Workspace, id=workspace_id)
    
    if request.method == 'POST' and request.POST.get('dir', None):
        file = workspace.get_file(request.POST.get('dir', None))
        
        if file:
            os.remove(file)
            return HttpResponse("deleted")

    return HttpResponse("error")

@can_edit()
def mkdir(request, workspace_id):
    """
    Create a new folder
    """
    workspace = get_object_or_404(Workspace, id=workspace_id)
    
    # build folder list
    folders = workspace.get_dir_tree()
    
    if request.method == 'POST':
        form = WorkspaceNewFolderForm(request.POST, folders=folders)
        if form.is_valid():
            # find absolute directory
            folder = workspace.get_dir(form.cleaned_data.get('folder', '/'))
            name = form.cleaned_data.get('name', 'newfolder')

            # create the directory
            if folder:
                os.mkdir(folder + name)
                return HttpResponse("created")
    else:
        form = WorkspaceNewFolderForm(folders=folders)
        
    return render_to_response("workspace/mkdir.html",
                              {'form': form,
                               'workspace': workspace},
                               context_instance=RequestContext(request))

@can_edit()
def rmdir(request, workspace_id):
    """
    Remove a folder
    """
    workspace = get_object_or_404(Workspace, id=workspace_id)
    
    # build folder list
    folders = workspace.get_dir_tree()
    
    if request.method == 'POST':
        form = WorkspaceMoveForm(request.POST, folders=folders)
        if form.is_valid():
            folder = workspace.get_dir(form.cleaned_data.get('folder', '/'))
            
            try:
                os.rmdir(folder)
            except:
                return HttpResponse("Cannot remove folder until it is empty")

            return HttpResponse("deleted")
    else:
        form = WorkspaceMoveForm(folders=folders)
        
    return render_to_response("workspace/rmdir.html",
                              {'form': form,
                               'workspace': workspace},
                               context_instance=RequestContext(request))

@can_view()
def preview(request, workspace_id):
    workspace = get_object_or_404(Workspace, id=workspace_id)
    if request.method == 'POST' and request.POST.get('dir', None):
        file = workspace.get_file(request.POST.get('dir', None))
    
        if file:
            # normalize the extension
            requestfile, ext = os.path.splitext(file)
            ext = ext[1:]
            if preview_aliases.get(ext, None):
                ext = preview_aliases[ext]
        
            # load up the preview template
            if ext in preview_extensions:
                return render_to_response("workspace/preview/%s.html" % ext,
                                          {'file': request.POST.get('dir', None),
                                           'workspace': workspace},
                                          context_instance=RequestContext(request))
    
    return HttpResponse("preview not available")

