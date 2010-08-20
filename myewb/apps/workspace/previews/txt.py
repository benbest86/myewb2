def render(file):
    f =  open(file, 'r')
    contents = f.read()
    f.close()
    return contents
