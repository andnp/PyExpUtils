from typing import Iterable, Iterator, Sequence, TypeVar, Union

# the most generic of generics
T = TypeVar('T')

ForAble = Union[Sequence[T], Iterable[T], Iterator[T]]

AnyNumber = Union[float, int]
