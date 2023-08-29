import numpy as np

from abc import abstractmethod
from typing import Callable, Generator

class Sampler:
    def next(self, v: float) -> float | None: ...
    def next_eval(self, v: Callable[[], float]) -> float | None: ...

    @abstractmethod
    def repeat(self, v: float, times: int) -> Generator[float, None, None]: ...
    def end(self) -> float | None: ...

class Ignore:
    def __init__(self): ...
    def next(self, v): return None
    def next_eval(self, v): return None
    def repeat(self, v, times): yield None
    def end(self): return None

class Identity(Sampler):
    def next(self, v: float):
        return v

    def next_eval(self, c: Callable[[], float]):
        return c()

    def repeat(self, v: float, times: int):
        for _ in range(times): yield v

    def end(self):
        return None


# --------------
# -- Samplers --
# --------------
class Window(Sampler):
    def __init__(self, size: int):
        self._b = np.empty(size, dtype=np.float64)
        self._clock = 0
        self._size = size

    def next(self, v: float):
        self._b[self._clock] = v
        self._clock += 1

        if self._clock == self._size:
            m = self._b.mean()
            self._clock = 0
            return m

    def next_eval(self, c: Callable[[], float]):
        return self.next(c())

    def repeat(self, v: float, times: int):
        while times > 0:
            r = self._size - self._clock
            r = min(times, r)

            # I can save a good chunk of compute if I know the whole window
            # is filled with v. Then the mean is clearly also v.
            if self._clock == 0 and r == self._size:
                times -= r
                yield v
                continue

            e = self._clock + r
            self._b[self._clock:e] = v
            self._clock = (self._clock + r) % self._size

            times -= r

            if self._clock == 0:
                yield self._b.mean()

    def end(self):
        out = None
        if self._clock > 0:
            out = self._b[:self._clock].mean()

        self._clock = 0
        return out

class Subsample(Sampler):
    def __init__(self, freq: int):
        self._clock = 0
        self._freq = freq

    def next(self, v: float):
        tick = self._clock % self._freq == 0
        self._clock += 1

        if tick:
            return v

    def next_eval(self, c: Callable[[], float]):
        tick = self._clock % self._freq == 0
        self._clock += 1

        if tick:
            return c()

    def repeat(self, v: float, times: int):
        if self._clock == 0:
            yield v

        r = self._clock + times
        reps = int(r // self._freq)
        for _ in range(reps):
            yield v

        self._clock = r % self._freq

    def end(self):
        self._clock = 0
        return None

class MovingAverage(Sampler):
    def __init__(self, decay: float):
        self._decay = decay
        self.z = 0.

    def next(self, v: float):
        self.z = self._decay * self.z + (1. - self._decay) * v
        return self.z

    def next_eval(self, c: Callable[[], float]):
        v = c()
        return self.next(v)

    def repeat(self, v: float, times: int):
        for _ in range(times):
            self.next(v)

    def end(self):
        return None
