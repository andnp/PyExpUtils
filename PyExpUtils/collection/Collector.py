from typing import Any, Callable, Dict, List
from PyExpUtils.collection.Sampler import Sampler, Ignore, Identity

"""doc
A frame-based data collection utility.
The collector stores some context---which index is currently being run, what is the current timestep, etc.---
and associates collected data with this context.

Example usage:
```python
collector = Collector(
  config={
    # a dictionary mapping keys -> data preprocessors
    # for instance performing fixed-window averaging
    'return': Window(100),
    # or subsampling 1 of every 100 values
    'reward': Subsample(100),
    # or moving averages
    'error': MovingAverage(0.99),
    # or ignored entirely
    'special': Ignore(),
  },
  # by default, if a key is not mentioned above it is stored as-is
  # however this can be changed by passing a default preprocessor
  default=Identity()
)

# tell the collector what idx of the experiment we are currently processing
collector.setIdx(0)

for step in range(exp.max_steps):
  # tell the collector to increment the frame
  collector.next_frame()

  # these values will be associated with the current idx and frame
  collector.collect('reward', r)
  collector.collect('error', delta)

  # not all values need to be stored at each frame
  if step % 100 == 0:
    collector.collect('special', 'test value')
```
"""
class Collector:
    def __init__(self, config: Dict[str, Sampler | Ignore] = {}, idx: int | None = None, default: Identity | Ignore = Identity()):
        self._d: List[Dict[str, Any]] = []
        self._c = config

        self._ignore = set(k for k, sampler in config.items() if isinstance(sampler, Ignore))
        self._sampler: Dict[str, Sampler] = {
            k: sampler for k, sampler in config.items() if not isinstance(sampler, Ignore)
        }

        self._idx: int | None = idx
        self._frame: int = -1
        self._cur: Dict[str, Any] = {}

        # create this once and cache it since it is stateless
        # avoid recreating on every step
        self._def = default

        # cache some useful metadata
        self._idxs = set[int]()
        self._keys = set[str]()

    # -------------
    # -- Context --
    # -------------
    def setIdx(self, idx: int):
        if self._idx is not None:
            self.reset()

        self._idxs.add(idx)
        self._idx = idx
        self._frame = -1
        self._cur = {}

    def getIdx(self):
        assert self._idx is not None
        return self._idx

    def next_frame(self):
        self._frame += 1

        if self._cur:
            self._cur['idx'] = self.getIdx()
            self._cur['frame'] = self._frame - 1
            self._d.append(self._cur)
            self._cur = {}

    def reset(self):
        self.next_frame()
        for k in self._sampler:
            v = self._sampler[k].end()
            if v is None: continue

            self._cur[k] = v

        self.next_frame()
        self._frame = -1
        self._cur = {}

    # -------------
    # -- Storing --
    # -------------
    def collect(self, name: str, value: Any):
        if name in self._ignore:
            return

        v = self._sampler.get(name, self._def).next(value)
        if v is None:
            return

        self._keys.add(name)
        self._cur[name] = v

    def evaluate(self, name: str, lmbda: Callable[[], Any]):
        if name in self._ignore:
            return

        v = self._sampler.get(name, self._def).next_eval(lmbda)
        if v is None:
            return

        self._keys.add(name)
        self._cur[name] = v

    # ---------------
    # -- Accessing --
    # ---------------
    def get(self, name: str, idx: int):
        out = [
            d[name] for d in self._d if d['idx'] == idx
        ]
        return out

    def get_frames(self, idx: int):
        return [ d for d in self._d if d['idx'] == idx ]

    def get_last(self, name: str):
        arr = self.get(name, self.getIdx())
        return arr[-1]

    def keys(self):
        return self._keys

    def indices(self):
        return self._idxs
