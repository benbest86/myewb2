"""myEWB workspace models

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada
"""

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models

import settings, os, shutil, datetime, re

# TODO: regex to use for validating filenames.  For now, anything not alpha-numeric-
# dash-underscore-period-space gets stripped, but would be good to allow accents eventually.
re_filename = re.compile(r'[^A-Za-z0-9\-_. ]')

class WorkspaceManager(models.Manager):
    def get_for_object(self, object):
        """
        Returns the workspace for a particular object (usually a group),
        creating one if needed.
        """
        w, c = self.get_query_set().get_or_create(content_type = ContentType.objects.get_for_model(object),
                                                  object_id = object.id)
        
        return w

class Workspace(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    
    objects = WorkspaceManager()

    # Get the filesystem directory for the workspace root, creating if needed
    def get_root(self):
        dir = os.path.join(settings.MEDIA_ROOT, 'workspace/files', str(self.id))
        if not os.path.isdir(dir):
            os.makedirs(dir, 0755)
        return dir
    
    # Get the filesystem directory for the workspace's preview cache,
    # creating if needed
    def get_cache_root(self):
        dir = os.path.join(settings.MEDIA_ROOT, 'workspace/cache', str(self.id))
        if not os.path.isdir(dir):
            os.makedirs(dir, 0755)
        return dir
    
    # Gets the filesystem directory for the given relative directory,
    # creating the filesystem root if needed.  If the requested directory
    # does not exist or contains invalid characters, False is returned.
    #
    # The optional cache flag indicates that we are creating a cache directory;
    # this changes the behaviour in a few ways:
    # - it uses the cache root instead of workspace root
    # - security-checking is relaxed to allow periods in the directory
    # - the directory is created if it does not exist instead of returning False
    def get_dir(self, dir, cache=False):
        if dir.find('.') > -1 and not cache:       # do not allow any periods
            return False

        if dir[0:1] != '/':
            dir = '/' + dir
        if dir[-1:] != '/':
            dir = dir + '/'
        
        if cache:
            dir = self.get_cache_root() + dir
        else:
            dir = self.get_root() + dir

        if os.path.isdir(dir):
            return dir
        elif cache:
            os.makedirs(dir, 0755)
            return dir
        else:
            return False
        
    # Gets the full filesystem path to a given file.
    # Returns False if the file does not exist or is invalid.  
    def get_file(self, filepath):
        if not filepath:
            return False
        
        # split into path and file
        dir, file = os.path.split(filepath)
        
        #  check validity of path
        fullpath = self.get_dir(dir)
        if fullpath:
            # check existance of file
            if os.path.isfile(fullpath + file):
                return fullpath + file
        
        return False
    
    # Get the cache directory for a given file.
    # Returns False if the file does not exist or is invalid.  
    def get_cache(self, filepath):
        if not filepath or not self.get_file(filepath):
            return False

        # get or create the cache directory
        # (no error checking, since self.get_file(filepath) should do all
        #  the checking we need)
        return self.get_dir(filepath, cache=True)
    
    # returns a list of the workspace's directory tree
    def get_dir_tree(self):
        folders, path = build_dir_tree('', self.get_root(), [], [], 0)
        return folders
    
    # check if this user can view the workspace
    #
    # This requires that the object owning the workspace implement a function
    # called workspace_view_perms(user); if this does not exist, permission
    # is implicitly granted.
    def user_can_view(self, user):
        parent = self.content_object
        if hasattr(parent, 'workspace_view_perms'):
            if not parent.workspace_view_perms(user):
                return False
        return True
    
    # check if this user can edit the workspace
    #
    # This requires that the object owning the workspace implement a function
    # called workspace_edit_perms(user); if this does not exist, view 
    # permissions are used
    def user_can_edit(self, user):
        parent = self.content_object
        if hasattr(parent, 'workspace_view_perms'):
            if not parent.workspace_edit_perms(user):
                return False
        else:
            return self.user_can_view(user)
        return True
    
    # Move a file in the workspace.
    # - src should be a WorkspaceFile object
    # - dst should be a relative path
    # returns a WorkspaceFile object referring to the new file, or False on failure
    def move_file(self, src, dst):
        # build paths
        absolute_dst = self.get_dir(dst)
        if absolute_dst:
            absolute_dst = absolute_dst + src.get_filename() 

            # move...
            os.rename(src.get_absolute_path(), absolute_dst)
            
            # update file metadata in the database
            src.update_folder(dst) 

            return src
        return False
    
    # Move a directory in the workspace.
    # - src and dst should be relative paths
    # returns a relative path to the dst folder, or False on failure
    def move_dir(self, src, dst):
        # get paths
        absolute_src = self.get_dir(src)
        absolute_dst = self.get_dir(dst)
        
        if absolute_src and absolute_dst and absolute_src != absolute_dst:
            absolute_src = absolute_src[0:-1]               # strip trailing slash
            _discard, name = os.path.split(absolute_src)    # find folder name
            absolute_dst = absolute_dst + name
        
            # move
            os.rename(absolute_src, absolute_dst)
            
            # move cache
            old_cache = self.get_dir(src, cache=True)
            old_cache = old_cache[0:-1]
            new_cache = self.get_dir(dst, cache=True)
            new_cache = new_cache + name
            os.renames(old_cache, new_cache)
            
            # normalize dst folder
            if dst[-1:] != '/':
                dst = dst + '/'
                
            return dst + name 
            
        return False
        
    # Rename a file in the workspace.
    # - src should be a WorkspaceFile object
    # - dstname should be a filename
    # returns a WorkspaceFile object referring to the new file, or False on failure
    def rename_file(self, src, dstname):
        # build paths
        absolute_dst = self.get_dir(src.get_folder())
        if absolute_dst:
            # TODO: security checks on filename
            # (can also be done in form validation instead of here... but for 
            #  now, this function isn't ever used so it doesn't matter much)
            
            absolute_dst = absolute_dst + dstname

            # move...
            os.rename(src.get_absolute_path(), absolute_dst)
            
            # update file metadata in the database
            src.update_name(dstname) 

            return src
        return False
    
    # Rename a directory in the workspace.
    # - src should be a relative path
    # - dstname should be a new name
    # returns a relative path to the dst folder, or False on failure
    def rename_dir(self, src, dstname):
        # get paths
        absolute_src = self.get_dir(src)
        
        if absolute_src:
            absolute_src = absolute_src[0:-1]               # strip trailing slash
            folder, name = os.path.split(absolute_src)      # find folder name
            absolute_dst = folder + '/' + dstname
        
            # move
            os.rename(absolute_src, absolute_dst)
            
            # move cache
            old_cache = self.get_dir(src, cache=True)
            old_cache = old_cache[0:-1]
            folder, name = os.path.split(old_cache)
            new_cache = folder + '/' + dstname
            os.renames(old_cache, new_cache)
            
            # normalize dst folder
            if src[-1:] == '/':
                src = src[0:-1]
            relpath, name = os.path.split(src)
            return relpath + '/' + dstname 
            
        return False
        
# recursive function to walk and build this workspace's file tree
def build_dir_tree(fname, dir, folders, path, counter):
    # currently in a directory?
    # (the counter is for paranoia, just in case an infinite loop gets created)
    if os.path.isdir(os.path.join(dir, fname)) and counter < 100:
        # add directory to path, and full path to list of folders
        path.append(fname)
        folders.append('/'.join(path))
        
        # build list of all contents
        subfolders = []
        for f in os.listdir(os.path.join(dir, fname)):
            subfolders.append(f)
            
        # sort.  WHY oh WHY doesn't os.listdir sort for you? :S
        subfolders.sort()
        
        # and go through, adding all the subdirectories as well
        for f in subfolders:
            folders, path = build_dir_tree(f, dir + '/' + fname, folders, path, counter+1)
        
        path.pop()
            
    return (folders, path)
    
class WorkspaceFileManager(models.Manager):
    # Take the uploaded file, and attach it to a new WorkspaceFile instance.
    # Takes four arguments:
    #  - the workspace that the file is being uploaded to
    #  - the path in the workspace
    #  - an UploadedFile object (typically, from request.FILES['file'])
    #  - the User uploading the file
    def upload(self, workspace, path, uploadedfile, user):
        # build relative name
        filename = uploadedfile.name
        if path[0:1] != '/':
            path = '/' + path
        if path[-1:] != '/':
            path = path + '/'
        relpath = path + filename
        
        # see if this file already exists (update, not create)
        workfile = self.load(workspace, relpath)
        if workfile:
            # shouldn't happen, but just in case...
            if not workfile.creator:
                workfile.creator = user
                workfile.save()
                
            # update metadata
            workfile.update(uploadedfile, user)

        else:
            # find absolute directory
            abspath = workspace.get_dir(path)
            
            # filename validation: strip out illegal characters
            escaped_filename = re_filename.sub(r'',
                                               filename)
            if escaped_filename != filename:
                relpath = path + escaped_filename
            
            # open file
            diskfile = open(abspath + escaped_filename, 'wb+')
            
            # write file to disk
            for chunk in uploadedfile.chunks():
                diskfile.write(chunk)
            diskfile.close() 

            # save metadata
            workfile = self.create(workspace=workspace,
                                   name=relpath,
                                   creator=user,
                                   updator=user)

        return workfile
        
    # Load a file from disk.
    # Workspace should be a workspace object, and filepath should be a relative 
    # path to the file from the workspace.
    #
    # If the file exists on disk but not meta-information is stored in the 
    # database, a record will be created for it.
    # (basically, a modified objects.get_or_create() for WorkspaceFile objects)
    #
    # If the file doesn't exist, return None
    
    def load(self, workspace, filepath):
        workfile = None
        try:
            workfile = self.get(workspace=workspace,
                                name=filepath)
        except WorkspaceFile.DoesNotExist:
            if workspace.get_file(filepath):
                workfile = self.create(workspace=workspace,
                                       name=filepath)
        except WorkspaceFile.MultipleObjectsReturned:
            workfile = self.filter(workspace=workspace,
                                    name=filepath)[0]
        return workfile

    def is_file(self, workspace, path):
        abs_path = workspace.get_file(path)
        if abs_path:
            return True
        else:
            return False
        
    def is_dir(self, workspace, path):
        abs_path = workspace.get_dir(path)
        if abs_path:
            return True
        else:
            return False

class WorkspaceFile(models.Model):
    workspace = models.ForeignKey(Workspace)
    name = models.CharField(max_length=255)
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    creator = models.ForeignKey(User, related_name='workspace_files', null=True)
    updator = models.ForeignKey(User, related_name='workspace_updates', null=True)
    
    objects = WorkspaceFileManager()
    
    def get_relative_path(self):
        return self.name
        
    def get_url(self):
        return os.path.join(settings.STATIC_URL, 'workspace/files', str(self.workspace.id)) + self.name
        
    def get_absolute_path(self):
        return self.workspace.get_file(self.name)
        
    def get_folder(self):
        path, filename = os.path.split(self.name)
        if path == '/':
            path = ''
        return path
    
    def get_cache_url(self):
        path, name = os.path.split(self.name)
        return os.path.join(settings.STATIC_URL, 'workspace/cache', str(self.workspace.id)) + self.name + '/'

    def get_cache_dir(self):
        return self.workspace.get_cache(self.name)
    
    def get_filename(self):
        path, filename = os.path.split(self.name)
        return filename
        
    def get_extension(self):
        filename, ext = os.path.splitext(self.name)
        return ext[1:]
        
    def get_size(self):
        return os.stat(self.get_absolute_path()).st_size
        
    # this does NOT perform the actual on-disk move, just updates the database path
    # (since folders can also be moved, the actual move code is in views.moveop()
    #  so that it can be re-used)
    def update_folder(self, new_folder):
        # normalize folder name (i do this so often, i should centralize it...)
        if new_folder[0:1] != '/':
            new_folder = '/' + new_folder
        if new_folder[-1:] != '/':
            new_folder = new_folder + '/'
            
        # ensure new dir exists and is valid...
        if self.workspace.get_dir(new_folder):
            old_cache = self.workspace.get_dir(self.get_relative_path(), cache=True)

            # update our metadata
            self.name = new_folder + self.get_filename()
            self.save()
            
            # update cached files
            new_cache = self.workspace.get_cache(self.get_relative_path())
            os.renames(old_cache, new_cache)
            
            return True
        return False
    
    # delete this file - deletes the file itself, the metadata record, cached
    # files, and revision history.  poof.  everything.  gone.
    def delete(self, *args, **kwargs):
        # clear cache
        cache = self.workspace.get_cache(self.get_relative_path())
        shutil.rmtree(cache, ignore_errors=True)
        
        # delete file
        os.remove(self.get_absolute_path())
        
        # delete revision history
        for r in self.workspacerevision_set.all():
            print r.delete()
        
        # calling super will delete this record
        return super(WorkspaceFile, self).delete(*args, **kwargs)
    
    # Replace this file with a newer version
    def update(self, uploadedfile, user):
        # create revision history record
        rev = WorkspaceRevision.objects.create(workspace=self.workspace,
                                               parent_file=self,
                                               date=self.modified,
                                               user=self.updator
                                               )
        rev_folder = datetime.date.today().strftime("%y/%m/")
        rev_folder = rev_folder + str(rev.id) + '/'
        rev_file = rev_folder + self.get_filename()
        
        rev.filename = rev_file
        rev.save()
        
        # save file to revision history
        old_cache = self.get_cache_dir()
        abspath = self.get_absolute_path()
        rev_dir = os.path.join(settings.MEDIA_ROOT, 'workspace/revisions', rev_folder)
        if not os.path.isdir(rev_dir):
            os.makedirs(rev_dir, 0755)
        os.rename(abspath, rev_dir + '/' + self.get_filename())
        
        # move cached files to history as well
        old_cache = old_cache[0:-1]             # strip trailing slash
        new_cache = rev.get_file().get_cache_dir()[0:-1]    # strip trailing slash
        if os.path.isdir(old_cache):
            os.rename(old_cache, new_cache)
        
        # open workspace file for writing - replace with uploaded file
        diskfile = open(abspath, 'wb+')
        for chunk in uploadedfile.chunks():
            diskfile.write(chunk)
        diskfile.close()
        
        # clear old cache
        # (TODO: create a queue to asynchronously generate cache files, and add this file to the queue)
        cache = self.workspace.get_cache(self.get_relative_path())
        shutil.rmtree(cache, ignore_errors=True)

        # update metadata
        self.updator = user
        self.save()
        
        return True
    
class WorkspaceRevision(models.Model):
    workspace = models.ForeignKey(Workspace)
    parent_file = models.ForeignKey(WorkspaceFile)
    
    date = models.DateTimeField()
    user = models.ForeignKey(User, null=True)
    reverted = models.ForeignKey('self', blank=True, null=True)
    
    filename = models.CharField(max_length=255, blank=True, null=True)
    
    # Returns an object that acts like a read-only WorkspaceFile, which 
    # represents this revision
    def get_file(self):
        return WorkspaceRevisionFile(self)

    # delete this revision - deletes the file itself, the metadata record, and 
    # cached files.  poof.  everything.  gone.
    def delete(self, *args, **kwargs):
        # clear cache
        cache = self.get_file().get_cache_dir()
        shutil.rmtree(cache, ignore_errors=True)
        
        # delete file
        os.remove(self.get_file().get_absolute_path())
        
        # calling super will delete this record
        return super(WorkspaceRevision, self).delete(*args, **kwargs)
    
    class Meta:
        ordering = ('-date', '-id')

# we don't extend WorkspaceFile because this doesn't need to be in the database
class WorkspaceRevisionFile:
    def __init__(self, revision):
        self.revision = revision
        
    def get_relative_path(self):
        return self.revision.filename
        
    def get_url(self):
        return os.path.join(settings.STATIC_URL, 'workspace/revisions', self.revision.filename)
        
    def get_absolute_path(self):
        return os.path.join(settings.MEDIA_ROOT, 'workspace/revisions', self.revision.filename) 
                            
    def get_cache_url(self):
        path, name = os.path.split(self.revision.filename)
        return os.path.join(settings.STATIC_URL, 'workspace/revisions_cache', path) + '/'
    
    def get_cache_dir(self):
        path, name = os.path.split(self.revision.filename)
        cache_root = os.path.join(settings.MEDIA_ROOT, 'workspace/revisions_cache', path)
        
        if not os.path.isdir(cache_root):
            os.makedirs(cache_root, 0755)
    
        return cache_root + '/'
    
    def get_folder(self):
        return self.revision.parent_file.get_folder()
    
    def get_filename(self):
        path, filename = os.path.split(self.revision.filename)
        return filename
        
    def get_extension(self):
        filename, ext = os.path.splitext(self.revision.filename)
        return ext[1:]
        
    def get_size(self):
        return os.stat(self.get_absolute_path()).st_size
