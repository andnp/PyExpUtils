import functools
from typing import Any, Callable, Dict

def memoize(f: Callable[[Any], Any], cache: Dict[Any, Any] = {}):
    def cacheKey(*args, **kwargs):
        s = ''
        for arg in args:
            s = s + '__' + str(arg)
        for arg in kwargs:
            s = s + '__' + str(arg) + '-' + str(kwargs[arg])
        return s

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        nonlocal cache
        nonlocal cacheKey
        key = cacheKey(*args, **kwargs)
        if key in cache:
            return cache[key]
        ret = f(*args, **kwargs)
        cache[key] = ret
        return ret

    return wrapped

def once(f: Callable[[], Any]):
    called = False
    ret = None
    def wrapped(*args, **kwargs):
        nonlocal called
        nonlocal ret
        if not called:
            ret = f(*args, **kwargs)
            called = True

        return ret

    return wrapped
