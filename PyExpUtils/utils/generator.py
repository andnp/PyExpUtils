from PyExpUtils.utils.types import AnyNumber, ForAble, T
import numpy as np
from typing import Generator, List, cast

# takes a generator and a number of items to group together
# returns a generator that yields `num` items in groups
# example:
# grouped = group(range(10), 3)
# grouped == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
def group(gen: ForAble[T], num: int) -> Generator[List[T], None, None]:
    coll: List[T] = []
    for x in gen:
        coll.append(x)
        if len(coll) == num:
            yield coll
            coll = []

    # if there was anything left over (generator was not perfectly divisible)
    # then go ahead an yield what was left and make sure to release it from memory
    if len(coll) > 0:
        yield coll
        coll = []

def windowAverage(arr: ForAble[AnyNumber], window: int) -> Generator[float, None, None]:
    for g in group(arr, window):
        yield cast(float, np.mean(g))
