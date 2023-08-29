from typing import Callable
from PyExpUtils.collection.Sampler import Sampler

class Pipe(Sampler):
    def __init__(self, *args: Sampler) -> None:
        self._subs = args

    def next(self, v: float) -> float | None:
        out: float | None = v
        for sub in self._subs:
            if out is None: return None
            out = sub.next(out)

        return out

    def next_eval(self, v: Callable[[], float]) -> float | None:
        subs = iter(self._subs)
        first = next(subs)
        out = first.next_eval(v)

        for sub in subs:
            if out is None: return None
            out = sub.next(out)

        return out

    def repeat(self, v: float, times: int):
        for _ in range(times):
            self.next(v)

    def end(self):
        return None
