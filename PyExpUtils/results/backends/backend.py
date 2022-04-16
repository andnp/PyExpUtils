from __future__ import annotations
from abc import abstractmethod
import numpy as np
from typing import Any, Callable, Optional, Sequence, Iterator, Union
from PyExpUtils.models.ExperimentDescription import ExperimentDescription
from PyExpUtils.utils.types import T


"""doc
The `Result` objects allows performing operations over results lazily so that many file system calls can be avoided.
This is extremely useful when doing large parameter sweeps and plotting over slices of parameters.
The object stores some metadata about the result that can be inferred from the experiment description without needing to open the result file.

```python
results = loadResults(exp, 'returns.npy') # -> gives an iterator over Result objects

for result in results:
    print(result.path) # -> 'results/MountainCar-v0/SARSA/alpha-1.0_lambda-1.0/returns.npy'
    print(result)

# only load results from disk where alpha > 0.2
results = filter(lambda res: res.params['alpha'] > 0.2, results)
for result in results:
    plot(result.load())
```
"""
class BaseResult:
    def __init__(self, path: str, exp: ExperimentDescription, idx: int):
        self.path = path
        self.exp = exp
        self.idx = idx
        self.params = exp.getPermutation(idx)[exp.getKeys()[0]]
        self._data: Optional[np.ndarray] = None

    # internal method that should be overridden for accessing datafiles
    @abstractmethod
    def _load(self) -> Any:
        pass

    # internal method that should be overridden to match expected data format
    # or to signal a null / missing result
    @abstractmethod
    def _default(self) -> np.ndarray:
        pass

    # cache the data after loading once
    # also fail semi-silently so that plotting scripts can continue even if results are missing
    def _lazyLoad(self):
        if self._data is not None:
            return self._data

        try:
            self._data = self._load()
            if self._data is None:
                raise Exception('Data did not load successfully')

            return self._data
        except Exception:
            print('Result not found :: ' + self.path)
            return self._default()

    """doc
    Takes a function that manipulates the result data.
    For example: useful for truncating data or looking at only final performance, etc.

    ```python
    def getFirstNSteps(results, n):
        for result in results:
            yield result.reducer(lambda data: data[0:n])

    results = loadResults(exp, 'returns.npy')
    results = getFirstNSteps(results, 100)
    ```
    """
    def reducer(self, lm: Callable[[np.ndarray], np.ndarray]):
        view = ResultView(self)
        view.reducer(lm)
        return view

    """doc
    Load the result from disk.
    The contents of the results file are cached, so as long as this result file is accessible (e.g. not garbage collected) you will only hit the filesystem once.
    This is important for distributed filesystems (like on computecanada) where filesystem calls are extremely expensive.

    Note that if the result does not exist (e.g. compute canada job timed out), then an error message will be printed but no exception will be thrown.
    This way plotting code can still continue to run with partial results.
    """
    def load(self):
        return self._lazyLoad()

    """doc
    Get the mean value over multiple runs from a result file.
    Defaults to assuming that results files are saved as `np.array([mean, stderr, runs])`.
    For different results file formats, override this method with a custom `Result` class.
    """
    @abstractmethod
    def mean(self) -> np.ndarray:
        pass

    """doc
    Get the standard error over multiple runs from a result file.
    Defaults to assuming that results files are saved as `np.array([mean, stderr, runs])`.
    For different results file formats, override this method with a custom `Result` class.
    """
    @abstractmethod
    def stderr(self) -> np.ndarray:
        pass

    # TODO: write docs
    @abstractmethod
    def runs(self) -> int:
        pass

"""doc
A "window" over a `Result` object that allows changing the type of reducer on the object while still referencing the same memory cache.
Useful for applying different views at the same results file without needing to load multiple copies of the result into memory or making multiple filesystem calls.
Returned from the `Result.reducer` method.
Maintains same API as a `Result` object and can be used interchangeably.

```python
results = loadResults(exp, 'returns.npy')
for result in results:
    view = result.reducer(lambda m: m.mean())
    view2 = result.reducer(lambda m: m.std())
```
"""
class ResultView(BaseResult):
    def __init__(self, result: BaseResult):
        self._result = result
        self._reducer = _identity
        self.idx = result.idx
        self.exp = result.exp
        self.params = result.params

    def _default(self):
        return self._result._default()

    def runs(self):
        return self._result.runs()

    def _load(self) -> Any:
        return self._result._load()

    def reducer(self, lm: Any):
        self._reducer = lm
        return self

    def load(self):
        return self._reducer(self._result.load())

    def mean(self):
        return self._reducer(self._result.mean())

    def stderr(self):
        return self._reducer(self._result.stderr())

ResultList = Union[Sequence[BaseResult], Iterator[BaseResult]]

def _identity(m: T) -> T:
    return m
