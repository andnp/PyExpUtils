import numpy as np
from abc import abstractmethod
from typing import Any, Callable, Dict, Generator, List, Optional
from PyExpUtils.utils.arrays import downsample, last, fillRest_
from PyExpUtils.utils.NestedDict import NestedDict

# ----------------
# -- Interfaces --
# ----------------
class _Sampler:
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

class Identity(_Sampler):
    def next(self, v: float):
        return v

    def next_eval(self, c: Callable[[], float]):
        return c()

    def repeat(self, v: float, times: int):
        for _ in range(times): yield v

    def end(self):
        return None

# ----------------
# -- Main logic --
# ----------------
class Collector:
    def __init__(self, config: Dict[str, _Sampler | Ignore] = {}, idx: Optional[int] = None, default: Identity | Ignore = Identity()):
        self._name_idx_data: NestedDict = NestedDict(depth=2, default=list)
        self._c = config

        self._ignore = set(k for k, sampler in config.items() if isinstance(sampler, Ignore))
        self._sampler: Dict[str, _Sampler] = {
            k: sampler for k, sampler in config.items() if not isinstance(sampler, Ignore)
        }

        self._idx: Optional[int] = idx

        # create this once and cache it since it is stateless
        # avoid recreating on every step
        self._def = default

    def setIdx(self, idx: int):
        if self._idx is not None:
            self.reset()

        self._idx = idx

    def getIdx(self):
        assert self._idx is not None
        return self._idx

    def get(self, name: str, idx: Optional[int] = None):
        if idx is not None:
            return self._name_idx_data[name, idx]

        all_idxs = self._name_idx_data[name]
        return list(all_idxs[k] for k in sorted(all_idxs.keys()))

    def keys(self):
        return self._name_idx_data.keys()

    def indices(self, key: str):
        return self._name_idx_data[key].keys()

    def fillRest(self, name: str, steps: int):
        idx = self.getIdx()
        arr = self._name_idx_data[name, idx]
        l = last(arr)
        fillRest_(arr, l, steps)

    def downsample(self, name: str, percent: Optional[float] = None, num: Optional[int] = None, method: str = 'window'):
        idxs = self._name_idx_data[name]
        for idx in idxs:
            data = idxs[idx]
            arr = downsample(data, percent, num, method)
            self._name_idx_data[name, idx] = arr

    def collect(self, name: str, value: Any):
        if name in self._ignore:
            return

        v = self._sampler.get(name, self._def).next(value)
        if v is None:
            return

        idx = self.getIdx()
        arr = self._name_idx_data[name, idx]
        arr.append(v)

    def repeat(self, name: str, value: float, times: int):
        if name in self._ignore:
            return

        vs = self._sampler.get(name, self._def).repeat(value, times)

        idx = self.getIdx()
        arr = self._name_idx_data[name, idx]
        for v in vs:
            arr.append(v)

    def concat(self, name: str, values: List[Any]):
        for v in values:
            self.collect(name, v)

    def evaluate(self, name: str, lmbda: Callable[[], Any]):
        if name in self._ignore:
            return

        v = self._sampler.get(name, self._def).next_eval(lmbda)
        if v is None:
            return

        idx = self.getIdx()
        arr = self._name_idx_data[name, idx]
        arr.append(v)

    def reset(self):
        for name in self._name_idx_data.keys():
            if name not in self._sampler:
                continue

            v = self._sampler[name].end()
            if v is None: continue
            idx = self.getIdx()
            arr = self._name_idx_data[name, idx]
            arr.append(v)

# --------------
# -- Samplers --
# --------------
class Window(_Sampler):
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

class Subsample(_Sampler):
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

class MovingAverage(_Sampler):
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
