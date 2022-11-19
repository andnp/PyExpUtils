from typing import Callable, Dict, Generic
from PyExpUtils.utils.types import T

Builder = Callable[[str], T]

class Cache(Generic[T]):
    def __init__(self) -> None:
        self.cache: Dict[str, T] = {}

    def get(self, key: str, builder: Builder[T]) -> T:
        got = self.cache.get(key)

        if got is not None:
            return got

        d = builder(key)
        self.cache[key] = d

        return d

    def set(self, key: str, val: T):
        self.cache[key] = val

    def delete(self, key: str):
        del self.cache[key]

    def empty(self):
        self.cache = {}
