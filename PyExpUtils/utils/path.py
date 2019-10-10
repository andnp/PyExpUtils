from PyExpUtils.utils.arrays import last

def rest(path):
    parts = path.split('/')
    return '/'.join(parts[1:])

def up(path):
    return '/'.join(path.split('/')[:-1])

def fileName(path):
    parts = path.split('/')
    f = last(parts)
    return f
