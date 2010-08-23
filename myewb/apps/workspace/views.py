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
from workspace.models import Workspace, WorkspaceFile
from workspace.forms import WorkspaceUploadForm, WorkspaceMoveForm, WorkspaceNewFolderForm, WorkspaceRenameForm

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
        file = WorkspaceFile.objects.load(workspace, request.POST['dir'])
        if file:
            return render_to_response("workspace/detail.html",
                                      {'workspace': workspace,
                                       'file': file},
                                      context_instance=RequestContext(request))
    return HttpResponse("error")
    
@can_view()
def folder_detail(request, workspace_id, folder=None, force_selection=False):
    """
    View the details of a folder
    """
    workspace = get_object_or_404(Workspace, id=workspace_id)
    
    response = []
    if request.method == 'POST':
        if folder:
            reldir = folder
        else:
            reldir = request.POST['dir']
        folder = workspace.get_dir(reldir)
        if folder:
            # build initial listing for current directory
            files = []
            dirs = []
            for f in os.listdir(folder):
                if os.path.isdir(os.path.join(folder, f)):
                    dirs.append(f)
                else:
                    files.append(f)
                    
            # sort lists
            dirs.sort()
            files.sort()
            
            if len(dirs) or len(files):
                i = 0
                # output directories...
                for f in dirs:
                    full_file = os.path.join(reldir, f)
                    response.append((full_file, '<li class="directory collapsed" id="%s">%s</li>' % (full_file, f)))
                    i = i + 1
                    
                # output files
                for f in files:
                    full_file = os.path.join(reldir, f)
                    fname, ext = os.path.splitext(f)
                    ext = ext[1:]
                    response.append((full_file, '<li class="file ext_%s" id="%s">%s</li>' % (ext, full_file, f)))

            path, foldername, ignore = reldir.rsplit('/', 2)

            return render_to_response("workspace/folder_detail.html",
                                      {'workspace': workspace,
                                       'foldername': foldername,
                                       'path': path,
                                       'listing': response,
                                       'relpath': reldir,
                                       'force_selection': force_selection},
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
            # save file
            file = WorkspaceFile.objects.upload(workspace,
                                                form.cleaned_data.get('folder', '/'),
                                                request.FILES['file'],
                                                request.user)
                                                
            # redirect to file info display
            return render_to_response("workspace/detail.html",
                                      {'workspace': workspace,
                                       'file': file,
                                       'force_selection': True},
                                      context_instance=RequestContext(request))
    else:
        form = WorkspaceUploadForm(folders=folders)
        
    return render_to_response("workspace/upload.html",
                              {'form': form,
                               'workspace': workspace},
                               context_instance=RequestContext(request))

@can_edit()
def bulk_move(request, workspace_id):
    workspace = get_object_or_404(Workspace, id=workspace_id)

    # build folder list
    folders = workspace.get_dir_tree()
    
    if request.method == 'POST':
        form = WorkspaceMoveForm(request.POST, folders=folders)
        if form.is_valid():
            dst = form.cleaned_data.get('folder', '/')
            filelist = request.POST.get('file', '')
            files = filelist.split(',')
            for f in files:
                if f and  WorkspaceFile.objects.is_file(workspace, f):
                    src = WorkspaceFile.objects.load(workspace, f)
                    dstfile = workspace.move_file(src, dst)
    
                elif f and WorkspaceFile.objects.is_dir(workspace, f):
                    dstdir = workspace.move_dir(f, dst)

            dst = dst + '/'
            return folder_detail(request, workspace_id=workspace_id, folder=dst, force_selection=True)
    return HttpResponse("error")    

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
            src = request.POST['file']
            dst = form.cleaned_data.get('folder', '/')
            
            if WorkspaceFile.objects.is_file(workspace, src):
                src = WorkspaceFile.objects.load(workspace, request.POST['file'])
                dstfile = workspace.move_file(src, dst)

                # redirect to detailed display
                if dstfile:
                    return render_to_response("workspace/detail.html",
                                              {'workspace': workspace,
                                               'file': dstfile,
                                               'force_selection': True},
                                              context_instance=RequestContext(request))
            elif WorkspaceFile.objects.is_dir(workspace, src):
                dstdir = workspace.move_dir(src, dst)
                dstdir = dstdir + '/'
                return folder_detail(request, workspace_id=workspace_id, folder=dstdir, force_selection=True)
    else:
        form = WorkspaceMoveForm(folders=folders)
        
    return render_to_response("workspace/move.html",
                              {'form': form,
                               'workspace': workspace},
                               context_instance=RequestContext(request))

@can_edit()
def rename(request, workspace_id):
    """
    Rename a file
    """
    workspace = get_object_or_404(Workspace, id=workspace_id)
    
    if request.method == 'POST':
        form = WorkspaceRenameForm(request.POST)
        if form.is_valid():
            # find absolute directory
            src = workspace.get_file(request.POST.get('file', None))        # src file, full path
            if not src:
                src = workspace.get_dir(request.POST.get('file', None))
                src = src[0:-1]                                             # strip trailing slash
            if src:
                leading, file = os.path.split(src)                          # src filename

                name = form.cleaned_data.get('newname', file)               # dst name
                dst = os.path.join(leading, name)                           # dst name, full path
            
            # do the rename!
            if src and dst and src != dst:
                os.rename(src, dst)
    
                # redirect to detailed display
                relpath, oldname = os.path.split(request.POST.get('file', '/'))
                if oldname == '':
                    relpath, oldname = os.path.split(relpath)
                relpath = relpath + '/' + name
                
                # file?
                if os.path.isfile(dst):
                    file = WorkspaceFile.objects.load(workspace, relpath)
                    if file:
                        return render_to_response("workspace/detail.html",
                                                  {'workspace': workspace,
                                                   'file': file,
                                                   'force_selection': True},
                                                  context_instance=RequestContext(request))
                # or folder?
                elif os.path.isdir(dst):
                    relpath = relpath + '/'
                    return folder_detail(request, workspace_id=workspace_id, folder=relpath, force_selection=True)
    else:
        form = WorkspaceRenameForm()
        
    return render_to_response("workspace/rename.html",
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
def bulk_delete(request, workspace_id):
    workspace = get_object_or_404(Workspace, id=workspace_id)

    if request.method == 'POST' and request.POST.get('files', None):
        filelist = request.POST.get('files', '')
        files = filelist.split(',')
        for f in files:
            if f:
                file = WorkspaceFile.objects.load(workspace, f)
                file.delete()

    return HttpResponse("done")

@can_edit()
def delete(request, workspace_id):
    """
    Delete a file
    """
    workspace = get_object_or_404(Workspace, id=workspace_id)
    
    if request.method == 'POST' and request.POST.get('dir', None):
        file = WorkspaceFile.objects.load(workspace, request.POST['dir'])
        
        if file:
            file.delete()
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
            cache = workspace.get_dir(form.cleaned_data.get('folder', '/'), cache=True)
            
            try:
                os.rmdir(folder)
            except:
                return HttpResponse("Cannot remove folder until it is empty")
            
            try:
                os.rmdir(cache)
            except:
                pass

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
        file = WorkspaceFile.objects.load(workspace, request.POST['dir'])
    
        if file:
            # normalize the extension
            ext = file.get_extension()
            if preview_aliases.get(ext, None):
                ext = preview_aliases[ext]
        
            # load up the preview template
            if ext in preview_extensions:
                return render_to_response("workspace/preview/%s.html" % ext,
                                          {'file': file,
                                           'workspace': workspace},
                                          context_instance=RequestContext(request))
    
    return HttpResponse("preview not available")

