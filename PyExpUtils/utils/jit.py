import logging
from typing import Any, Callable, TypeVar

_has_warned = False
T = TypeVar('T', bound=Callable[..., Any])

def try2jit(f: T) -> T:
    try:
        from numba import njit
        return njit(f, cache=True, nogil=True, fastmath=True)
    except Exception:
        global _has_warned
        if not _has_warned:
            _has_warned = True
            logging.getLogger('PyExpUtils').warn('Could not jit compile --- expect slow performance')

        return f
