from PyExpUtils.utils.types import ForAble, T
from itertools import tee, filterfalse
from typing import Callable, List, Sequence, Union, Iterator

def fillRest(arr: List[T], val: T, length: int) -> List[T]:
    for _ in range(len(arr), length):
        arr.append(val)

    return arr

def first(listOrGen: Union[Sequence[T], Iterator[T]]):
    if isinstance(listOrGen, Sequence):
        return listOrGen[0]

    return next(listOrGen)

def last(l: Sequence[T]):
    return l[len(l) - 1]

def partition(gen: ForAble[T], pred: Callable[[T], bool]):
    t1, t2 = tee(gen)

    return filter(pred, t2), filterfalse(pred, t1)
