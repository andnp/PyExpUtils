from typing import Iterable, TypeVar, cast

T = TypeVar('T')
def filter_none(it: Iterable[T | None]) -> Iterable[T]:
    out = filter(lambda x: x is not None, it)
    return cast(Iterable[T], out)
