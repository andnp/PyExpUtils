import numpy as np
from itertools import tee, filterfalse
from typing import Any, Callable, List, Sequence, Union, Iterator, Optional
from PyExpUtils.utils.jit import try2jit
from PyExpUtils.utils.generator import windowAverage
from PyExpUtils.utils.types import AnyNumber, ForAble, T

def npPadUneven(arr: Sequence[np.ndarray], val: float) -> np.ndarray:
    longest = len(arr[0])
    for sub in arr:
        l = sub.shape[0]
        if l > longest:
            longest = l

    out = np.empty((len(arr), longest))
    for i, sub in enumerate(arr):
        out[i] = np.pad(sub, (0, longest - sub.shape[0]), constant_values=val)

    return out

def padUneven(arr: List[List[T]], val: T) -> List[List[T]]:
    longest = len(arr[0])
    for sub in arr:
        l = len(sub)
        if l > longest:
            longest = l

    out: List[List[T]] = []
    for sub in arr:
        out.append(fillRest(sub, val, longest))

    return out

def fillRest(arr: List[T], val: T, length: int) -> List[T]:
    if len(arr) >= length:
        return arr

    rem = length - len(arr)
    pad = [val] * rem

    return arr + pad

def fillRest_(arr: List[T], val: T, length: int) -> List[T]:
    for _ in range(len(arr), length):
        arr.append(val)

    return arr

def first(listOrGen: Union[Sequence[T], Iterator[T]]):
    if isinstance(listOrGen, Sequence):
        return listOrGen[0]

    return next(listOrGen)

def last(l: Sequence[T]) -> T:
    return l[len(l) - 1]

def partition(gen: ForAble[T], pred: Callable[[T], bool]):
    t1, t2 = tee(gen)

    return filter(pred, t2), filterfalse(pred, t1)

def deduplicate(arr: Sequence[T]) -> List[T]:
    return list(set(arr))

def unwrap(arr: List[T]) -> Union[T, List[T]]:
    if len(arr) == 1:
        return arr[0]

    return arr

def sampleFrequency(arr: Sequence[Any], percent: Optional[float] = None, num: Optional[int] = None):
    if percent is None and num is None:
        raise Exception()

    if percent is not None:
        num = int(len(arr) * percent)

    if num is None:
        raise Exception('impossible to reach')

    every = int(len(arr) // num)

    return every

def downsample(arr: Sequence[AnyNumber], percent: Optional[float] = None, num: Optional[int] = None, method: str = 'window'):
    every = sampleFrequency(arr, percent, num)

    if every <= 1:
        return arr

    if method == 'subsample':
        return [arr[i] for i in range(0, len(arr), every)]

    elif method == 'window':
        out = list(windowAverage(arr, every))

        # this case might occur if the array is not evenly divisible by num
        # then we should end up with exactly one additional element in out
        # which does not have a complete window average. Just toss it
        if num is not None and len(out) > num:
            return out[:num]

        return out

    else:
        raise Exception()

@try2jit
def argsmax(arr: np.ndarray):
    ties: List[int] = [0 for _ in range(0)]  # <-- trick njit into knowing the type of this empty list
    top: float = arr[0]

    for i in range(len(arr)):
        if arr[i] > top:
            ties = [i]
            top = arr[i]

        elif arr[i] == top:
            ties.append(i)

    if len(ties) == 0:
        ties = list(range(len(arr)))

    return ties

@try2jit
def argsmax2(arr: np.ndarray):
    ties: List[List[int]] = []
    for i in range(arr.shape[0]):
        ties.append(argsmax(arr[i]))

    return ties
