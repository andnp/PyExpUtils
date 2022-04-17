from __future__ import annotations
from typing import Any, Callable, Dict, Generator, Generic, Optional, Tuple, TypeVar, Union

K = TypeVar('K', bound=Union[int, str])
V = TypeVar('V')
R = TypeVar('R')

Key = Union[K, Tuple[K, ...]]
class NestedDict(Generic[K, V]):
    def __init__(self, depth: int, default: Optional[Callable[[], V]] = None):
        self._depth = depth
        self._default = default
        self._data: Dict[K, Any] = {}

    def __getitem__(self, keys: Key[K]) -> Any:
        keys = self._normalize(keys)
        assert len(keys) <= self._depth

        has_ellipse = ... in keys

        # easy case: we directly access a single element
        if not has_ellipse:
            level: Any = self._data
            for key in keys[:-1]:
                if key not in level:
                    level[key] = {}

                level = level[key]

            if keys[-1] not in level and self._default is not None:
                level[keys[-1]] = self._default()

            return level[keys[-1]]

        out = {}
        idx = keys.index(...)
        level = self._data
        for i in range(idx):
            key = keys[i]
            level = level[key]

        start = level
        for dkey in start:
            level = start[dkey]
            for i in range(idx + 1, len(keys)):
                key = keys[i]
                level = level[key]

            out[dkey] = level

        return out

    def __setitem__(self, keys: Key[K], val: V):
        keys = self._normalize(keys)
        assert len(keys) == self._depth

        level = self._data
        for key in keys[:-1]:
            nlevel = level.get(key, {})
            level[key] = nlevel

            level = nlevel

        level[keys[-1]] = val

    def __iter__(self) -> Generator[Tuple[K, ...], None, None]:
        return _walkKeys(self._data)

    def __contains__(self, keys: Key[K]):
        keys = self._normalize(keys)
        assert len(keys) <= self._depth

        level = self._data
        for key in keys:
            if key not in level: return False

            level = level[key]

        return True

    def map(self, f: Callable[[V], R]) -> NestedDict[K, R]:
        out = NestedDict[K, R](self._depth)

        for key in self:
            out[key] = f(self[key])

        return out

    def keys(self):
        return self._data.keys()

    def _normalize(self, key: Key[K]) -> Tuple[K, ...]:
        if isinstance(key, tuple):
            return key

        return (key, )

    @classmethod
    def fromDict(cls, d: Dict[K, Any]):
        depth = 0
        node = d
        while isinstance(node, dict):
            k = next(iter(node.keys()))
            node = node[k]
            depth += 1

        out = cls(depth)
        out._data = d

        return out

def _walkKeys(d: Dict[K, Any]) -> Generator[Tuple[K, ...], None, None]:
    for k in d:
        if not isinstance(d[k], dict):
            yield (k, )
            continue

        for tup in _walkKeys(d[k]):
            yield (k, ) + tup
