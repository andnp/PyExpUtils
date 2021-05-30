import numpy as np
from typing import Dict, TypeVar, Generic

T = TypeVar('T')

class CircularBuffer(Generic[T]):
    def __init__(self, buffer_size: int) -> None:
        self.buffer_size = buffer_size

        self._items = 0
        self._idx = 0
        self.buffer: Dict[int, T] = {}

    def __len__(self):
        return self._items

    def add(self, item: T):
        self.buffer[self._idx] = item

        if len(self) < self.buffer_size:
            self._items += 1

        self._idx = (self._idx + 1) % self.buffer_size

    def sample(self, batch_size: int = 1):
        indices = np.random.permutation(len(self))
        return [self.buffer[indices[i]] for i in range(batch_size)]
