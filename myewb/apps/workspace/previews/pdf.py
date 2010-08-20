import os
import settings
import subprocess

def render(workspace, filepath):
    preview = workspace.get_cache(filepath)
    if preview:
        fpath, fname = os.path.split(filepath)
        fname = fname + ".html"
        
        cache_file = preview + fname
        
        # attempt to create cache
        # (TODO: we shuold really do this after uploading, or on a nightly cron)
        if not os.path.isfile(cache_file):
            print "trying to generate cache"
            cache(workspace, filepath)

        if os.path.isfile(cache_file):
            return '%sworkspace/cache/%s%s/%s' % (settings.STATIC_URL, str(workspace.id), filepath, fname)
        
    return ""

def cache(workspace, filepath):
    print "woot?"
    preview = workspace.get_cache(filepath)
    if preview:
        fpath, fname = os.path.split(filepath)
        fname = fname + ".html"
        
        cache_file = preview + fname
        file = workspace.get_file(filepath)
        if os.path.isfile(file):
            filestat = os.stat(file)

            cachestat = None
            if os.path.isfile(cache_file):
                cachestat = os.stat(cache_file)
            
            # check modified time to see if cached copy is stale
            if not cachestat or filestat.st_mtime > cache_file.st_mtime:
                print "trying to convert", file, "to", cache_file
                ret = subprocess.call(['pdftohtml', '-noframes', file, cache_file])
                print "ret", ret
