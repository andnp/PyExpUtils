from typing import Any, Callable, Dict, List, Optional
from PyExpUtils.utils.arrays import downsample, last, fillRest_
from PyExpUtils.utils.NestedDict import NestedDict

class Collector:
    def __init__(self, idx: Optional[int] = None):
        self._name_idx_data: NestedDict = NestedDict(depth=2, default=list)

        self.sample_rate: Dict[str, int] = {}
        self.sample_clock: Dict[str, int] = {}

        self._idx: Optional[int] = idx

    def setIdx(self, idx: int):
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
        sample_rate = self.sample_rate.get(name, 1)
        sample_clock = self.sample_clock.get(name, 0)
        self.sample_clock[name] = sample_clock + 1

        if sample_clock % sample_rate > 0:
            return

        idx = self.getIdx()
        arr = self._name_idx_data[name, idx]
        arr.append(value)

    def concat(self, name: str, values: List[Any]):
        if name in self.sample_rate:
            # don't just append to the array
            # we need to make sure we respect sample rates
            for v in values:
                self.collect(name, v)

            return

        # otherwise, we can be smart and avoid a linear cost
        idx = self.getIdx()
        arr = self._name_idx_data[name, idx]
        arr.extend(values)

    def evaluate(self, name: str, lmbda: Callable[[], Any]):
        sample_rate = self.sample_rate.get(name, 1)
        sample_clock = self.sample_clock.get(name, 0)
        self.sample_clock[name] = sample_clock + 1

        if sample_clock % sample_rate > 0:
            return

        value = lmbda()
        idx = self.getIdx()
        arr = self._name_idx_data[name, idx]
        arr.append(value)

    def setSampleRate(self, name: str, every: int):
        self.sample_rate[name] = every
        self.sample_clock[name] = 0
