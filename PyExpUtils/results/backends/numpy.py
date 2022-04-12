import numpy as np
from typing import Any, Generator, Type
from PyExpUtils.results.paths import listResultsPaths
from PyExpUtils.models.ExperimentDescription import ExperimentDescription
from PyExpUtils.results.backends.backend import BaseResult, ResultView
from PyExpUtils.utils.cache import Cache

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
class Result(BaseResult):
    # internal method that should be overridden for accessing datafiles
    def _load(self):
        data = np.load(self.path, allow_pickle=True)
        return np.array(data)

    # internal method that should be overridden to match expected data format
    # or to signal a null / missing result
    def _default(self):
        return np.array((np.NaN, np.NaN, 0))

    # cache the data after loading once
    # also fail semi-silently so that plotting scripts can continue even if results are missing
    def _lazyLoad(self):
        if self._data is not None:
            return self._data

        try:
            self._data = self._load()
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
    def reducer(self, lm: Any):
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
    def mean(self):
        return self.load()[0]

    """doc
    Get the standard error over multiple runs from a result file.
    Defaults to assuming that results files are saved as `np.array([mean, stderr, runs])`.
    For different results file formats, override this method with a custom `Result` class.
    """
    def stderr(self):
        return self.load()[1]


_result_cache = Cache[Result]()

"""doc
Returns an iterator over all results that are expected to exist given a particular experiment.
Takes the `ExperimentDescription` and the name of the result file.
Does not load results from disk.

```python
results = loadResults(exp, 'returns.npy')

for result in results:
    print(result) # -> `<Result>`
```
"""
def loadResults(exp: ExperimentDescription, result_file: str, base: str = './', cache: bool = True, ResultClass: Type[Result] = Result) -> Generator[Result, Any, Any]:
    for i, path in enumerate(listResultsPaths(exp)):
        summary_path = base + '/' + path + '/' + result_file

        if cache:
            yield _result_cache.get(summary_path, lambda path: ResultClass(path, exp, i))

        else:
            yield ResultClass(summary_path, exp, i)


def saveResults(exp: ExperimentDescription, idx: int, filename: str, data: Any, base: str = './'):
    save_context = exp.buildSaveContext(idx, base=base)
    save_context.ensureExists()

    np_file = save_context.resolve(f'{filename}.npy')
    np.save(np_file, np.asarray(data, dtype=object))

    return np_file
