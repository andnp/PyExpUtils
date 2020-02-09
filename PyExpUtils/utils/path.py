from PyExpUtils.utils.arrays import last
from collections.abc import Iterable

def rest(path):
    parts = path.split('/')
    return '/'.join(parts[1:])

def up(path):
    return '/'.join(path.split('/')[:-1])

def fileName(path):
    parts = path.split('/')
    f = last(parts)
    return f

def removeFirstAndLastSlash(s):
    if s.startswith('/'):
        s = s[1:]

    if s.endswith('/'):
        s = s[:-1]

    return s

def join(*argv):
    if isinstance(argv[0], Iterable) and type(argv[0]) is not str:
        argv = argv[0]

    not_empty = filter(lambda s: s != '', argv)
    no_slashes = map(removeFirstAndLastSlash, not_empty)

    path = '/'.join(no_slashes)

    if argv[0].startswith('/'):
        path = '/' + path

    return path