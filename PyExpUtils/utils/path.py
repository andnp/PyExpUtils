def rest(path):
    parts = path.split('/')
    return '/'.join(parts[1:])
