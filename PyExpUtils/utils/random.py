import numpy as np
from typing import Sequence, TypeVar
from PyExpUtils.utils.arrays import argsmax
from PyExpUtils.utils.jit import try2jit

T = TypeVar('T')

# way faster than np.random.choice
# arr is an array of probabilities, should sum to 1
@try2jit
def sample(arr: np.ndarray, rng: np.random.Generator):
    r = rng.random()
    s = 0
    for i, p in enumerate(arr):
        s += p
        if s > r or s == 1:
            return i

    # worst case if we run into floating point error, just return the last element
    # we should never get here
    return len(arr) - 1

# also much faster than np.random.choice
# choose an element from a list with uniform random probability
@try2jit
def choice(arr: Sequence[T], rng: np.random.Generator) -> T:
    idxs = rng.permutation(len(arr))
    return arr[idxs[0]]

# argmax that breaks ties randomly
@try2jit
def argmax(vals: np.ndarray, rng: np.random.Generator):
    ties = argsmax(vals)
    return choice(ties, rng)
