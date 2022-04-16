import concurrent.futures as cf
from typing import Callable, Generator, Sequence, TypeVar

T = TypeVar('T')
R = TypeVar('R')
def threadMap(f: Callable[[T], R], arr: Sequence[T]) -> Generator[R, None, None]:
    with cf.ThreadPoolExecutor(max_workers=8) as executor:
        futures = (executor.submit(f, x) for x in arr)
        for future in cf.as_completed(futures):
            yield future.result()
