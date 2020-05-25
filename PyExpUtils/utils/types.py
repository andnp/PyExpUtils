import numpy as np
from typing import Any, Callable, Iterable, Iterator, Optional, Sequence, TypeVar, Union

# the most generic of generics
T = TypeVar('T')

ForAble = Union[Sequence[T], Iterable[T], Iterator[T]]

AnyNumber = Union[float, int]
NpList = Union[np.ndarray, Sequence[AnyNumber]]

def optionalCast(typ: Callable[[Any], T], thing: Optional[Any]) -> Optional[T]:
    if thing is None:
        return thing

    return typ(thing)
