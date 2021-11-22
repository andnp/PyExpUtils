import re
from typing import Iterable
from PyExpUtils.utils.arrays import last

def split(path: str):
    parts = path.split('/')

    # if path starts with leading slash, then make sure that doesn't go away from split('/')
    if parts[0] == '':
        parts[0] = '/'

    return parts

def rest(path: str):
    parts = split(path)
    return join(*parts[1:])

def up(path: str):
    return join(*split(path)[:-1])

def fileName(path: str):
    parts = split(path)
    f = last(parts)
    return f

def removeFirstAndLastSlash(s: str):
    if s.startswith('/'):
        s = s[1:]

    if s.endswith('/'):
        s = s[:-1]

    return s

def remoteDuplicatedSlashes(s: str):
    return re.sub(r'/+', '/', s)

def join(*argv: str):
    # remote empty strings
    gen: Iterable[str] = filter(lambda s: s != '', argv)
    # remote any duplicated slashes, e.g. this//is/a/path
    gen = map(remoteDuplicatedSlashes, gen)
    # get rid of leading/trailing slashes
    gen = map(removeFirstAndLastSlash, gen)
    # make sure there are no empty strings after cleaning up slashes
    gen = filter(lambda s: s != '', gen)

    path = '/'.join(gen)

    if argv[0].startswith('/'):
        path = '/' + path

    return path
