import functools
from typing import Any, Callable, Dict, TypeVar, cast

F = TypeVar('F', bound=Callable[..., Any])
T = TypeVar('T')
R = TypeVar('R')

def memoize(f: F, cache: Dict[str, Any] = {}) -> F:
    def cacheKey(*args: Any, **kwargs: Any):
        s = ''
        for arg in args:
            s = s + '__' + str(arg)
        for arg in kwargs:
            s = s + '__' + str(arg) + '-' + str(kwargs[arg])
        return s

    @functools.wraps(f)
    def wrapped(*args: Any, **kwargs: Any):
        nonlocal cache
        nonlocal cacheKey
        key = cacheKey(*args, **kwargs)
        if key in cache:
            return cache[key]
        ret = f(*args, **kwargs)
        cache[key] = ret
        return ret

    return cast(F, wrapped)

def once(f: Callable[[], R]) -> Callable[[], R]:
    called = False
    ret = None

    def wrapped() -> R:
        nonlocal called
        nonlocal ret
        if not called:
            ret = f()
            called = True

        # have to cast this because control flow analysis thinks this is type R | None
        # since R _could_ contain None, there is no clean way to signal to the type-checker
        # that what we are doing is okay. So instead we override.
        return cast(R, ret)

    return wrapped
