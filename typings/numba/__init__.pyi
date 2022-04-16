# from typing import Callable
from typing import Callable, overload
from PyExpUtils.utils.types import T

@overload
def njit(cache: bool = False, parallel: bool = False, nogil: bool = False, fastmath: bool = False) -> Callable[[T], T]: ...
@overload
def njit(f: T, cache: bool = False, parallel: bool = False, nogil: bool = False, fastmath: bool = False) -> T: ...

def jit(cache: bool, forceobj: bool) -> Callable[[T], T]: ...
