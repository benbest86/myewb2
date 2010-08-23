def render(workspace, file):
    
    f =  open(file.get_absolute_path(), 'r')
    contents = f.read()
    f.close()
    return contents
