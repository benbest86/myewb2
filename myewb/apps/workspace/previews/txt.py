def render(workspace, filepath):
    file = workspace.get_file(filepath)
    
    f =  open(file, 'r')
    contents = f.read()
    f.close()
    return contents
