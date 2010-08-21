import os
import settings
import subprocess
import time

def render(workspace, filepath):
    preview = workspace.get_cache(filepath)
    if preview:
        fpath, fname = os.path.split(filepath)
        fname = fname + ".html"
        
        cache_file = preview + fname
        
        # attempt to create cache
        # (TODO: we shuold really do this after uploading, or on a nightly cron)
        if not os.path.isfile(cache_file):
            cache(workspace, filepath)

        if os.path.isfile(cache_file):
            return '%sworkspace/cache/%s%s/%s' % (settings.STATIC_URL, str(workspace.id), filepath, fname)
        
    return ""

def cache(workspace, filepath):
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
            
            # if cache already exists, no need to do anything
            if cachestat and filestat.st_mtime <= cachestat.st_mtime:
                return True
            
            # attempt to generate cache file
            #ret = subprocess.call(['pdftohtml', '-noframes', file, cache_file])
            ret = subprocess.call(['wvHtml', file, cache_file])
            
            # ret == 0 for success
            if ret == 0:
                # add some CSS and stuff to the file
                htmlfile = open(cache_file, 'r')
                new_contents = []
                for line in htmlfile:
                    if line[0:7] == '</head>':
                        new_contents.append('<link rel="stylesheet" href="/site_media/static/css/document.css" />\n')
                    elif line[0:7] == '</body>':
                        new_contents.append('</div>\n')
                        
                    new_contents.append(line)
                    
                    if line[0:5] == '<body':
                        new_contents.append('<div id="docbody">\n')
                htmlfile.close()
                
                htmlfile = open(cache_file, 'w')
                htmlfile.write(''.join(new_contents))
                htmlfile.close()
                
                return True
                
    return False