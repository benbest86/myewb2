"""myEWB group workspaces

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

Last modified on 2010-08-18
@author Francis Kung
"""

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse

from workspace.models import Workspace
from workspace.forms import WorkspaceUploadForm, WorkspaceMoveForm, WorkspaceNewFolderForm

import settings, os

preview_extensions = ['jpg']
preview_aliases = {'jpeg': 'jpg',
                   'gif': 'jpg',
                   'png': 'jpg',
                   'ico': 'jpg',
                   'bmp': 'jpg'}

def browse(request, workspace_id):
    """
    Browse a group's workspace
    """
    workspace = get_object_or_404(Workspace, id=workspace_id)
    
    response = []
    if request.method == 'POST':
        reldir = request.POST.get('dir', '/')
        dir = workspace.get_dir(reldir)
        
        # build directory listing
        if dir:
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
                
            response = ['<ul class="jqueryFileTree" style="display: none;">']
            if len(dirs) or len(files):
                
                # output directories...
                for f in dirs:
                    full_file = os.path.join(reldir, f)
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
        
    # return listing
    return HttpResponse(''.join(response))

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
            file = dir + filename
            stat = os.stat(file)
            return render_to_response("workspace/detail.html",
                                      {'workspace': workspace,
                                       'path': folder,
                                       'filename': filename,
                                       'relpath': file,
                                       'stat': stat},
                                      context_instance=RequestContext(request))
    else:
        form = WorkspaceUploadForm(folders=folders)
        
    return render_to_response("workspace/upload.html",
                              {'form': form,
                               'workspace': workspace},
                               context_instance=RequestContext(request))

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
                filepath = folder + file
                stat = os.stat(dst)
                return render_to_response("workspace/detail.html",
                                          {'workspace': workspace,
                                           'path': folder,
                                           'filename': file,
                                           'relpath': filepath,
                                           'stat': stat},
                                          context_instance=RequestContext(request))
    else:
        form = WorkspaceMoveForm(folders=folders)
        
    return render_to_response("workspace/move.html",
                              {'form': form,
                               'workspace': workspace},
                               context_instance=RequestContext(request))

def replace(request, workspace_id):
    """
    View the details of a file
    """
    workspace = get_object_or_404(Workspace, id=workspace_id)
    return HttpResponse("not implemented")

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
