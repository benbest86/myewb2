import os
import settings
import subprocess

def render(file):
    preview = file.get_cache_dir()
    if preview:
        fname = file.get_filename() + ".html"
        
        cache_file = preview + fname
        
        # attempt to create cache
        # (TODO: we shuold really do this after uploading, or on a nightly cron)
        if not os.path.isfile(cache_file):
            cache(file)

        if os.path.isfile(cache_file):
            return file.get_cache_url() + fname
        
    return ""

def cache(file):
    preview = file.get_cache_dir()
    if preview:
        fname = file.get_filename() + ".html"
        
        cache_file = preview + fname
        file = file.get_absolute_path()
        if os.path.isfile(file):
            filestat = os.stat(file)

            cachestat = None
            if os.path.isfile(cache_file):
                cachestat = os.stat(cache_file)
            
            # if cache already exists, no need to do anything
            if cachestat and filestat.st_mtime <= cachestat.st_mtime:
                return True
            
            # attempt to generate cache file
            ret = subprocess.Popen(['pdftohtml', '-noframes', file, cache_file], cwd=preview)
            ret.wait()
            ret = ret.returncode
            
            # ret == 0 for success
            if ret == 0:
                # add some CSS and stuff to the file
                htmlfile = open(cache_file, 'r')
                new_contents = []
                for line in htmlfile:
                    if line[0:7] == '</HEAD>':
                        new_contents.append('<link rel="stylesheet" href="/site_media/static/css/document.css" />\n')
                    elif line[0:7] == '</BODY>':
                        new_contents.append('</div>\n')
                        
                    new_contents.append(line)
                    
                    if line[0:5] == '<BODY':
                        new_contents.append('<div id="docbody">\n')
                htmlfile.close()
                
                htmlfile = open(cache_file, 'w')
                htmlfile.write(''.join(new_contents))
                htmlfile.close()
                
                return True
                
    return False