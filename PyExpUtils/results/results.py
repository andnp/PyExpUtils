import numpy as np
from typing import Any, Callable, Dict, Generator, List, Optional, Type
from PyExpUtils.models.ExperimentDescription import ExperimentDescription
from PyExpUtils.utils.arrays import first
from PyExpUtils.utils.dict import equal, get, partialEqual
from PyExpUtils.results.backends.backend import BaseResult, ResultList
import PyExpUtils.results.backends.csv as CsvBackend
import PyExpUtils.results.backends.h5 as H5Backend

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
def loadResults(exp: ExperimentDescription, result_file: str, base: str = './', cache: bool = True, ResultClass: Type[BaseResult] = BaseResult) -> Generator[BaseResult, Any, Any]:
    # try to guess what backend to use
    backend = 'csv'
    # first check the file ending to get a hint
    if result_file.endswith('.npy'):
        backend = 'numpy'
    elif result_file.endswith('.h5'):
        backend = 'h5'

    # but override that if a class is specified
    # trust the caller knows what they're doing if this is specified
    if issubclass(ResultClass, CsvBackend.Result):
        return CsvBackend.loadResults(exp, result_file, base, cache, ResultClass)

    elif issubclass(ResultClass, H5Backend.H5Result):
        return H5Backend.loadResults(exp, result_file, base, cache, ResultClass)

    if backend == 'csv':
        return CsvBackend.loadResults(exp, result_file, base, cache)

    elif backend == 'h5':
        return H5Backend.loadResults(exp, result_file, base, cache)

    else:
        raise NotImplementedError(f'Unknown backend encountered: {backend}')

"""doc
Save a set of results to file, using the file extension to determine the saving backend
"""
def saveResults(exp: ExperimentDescription, idx: int, filename: str, data: Any, base: str = './'):
    if filename.endswith('.csv'):
        return CsvBackend.saveResults(exp, idx, filename, data, base)
    elif filename.endswith('.h5'):
        return H5Backend.saveResults(exp, idx, filename, data, base)

    raise NotImplementedError(f'Unknown backend encountered: {filename}')

"""doc
Utility function for sorting results into bins based on values of a metaParameter.
Does not load results from disk.

```python
results = loadResults(exp, 'returns.npy')
bins = splitOverParameter(results, 'alpha')
print(bins) # -> { 1.0: [Result, Result, ...], 0.5: [Result, Result, ...], 0.25: [Result, Result, ...], ...}
```
"""
def splitOverParameter(results: ResultList, param: str):
    parts: Dict[Any, List[BaseResult]] = {}
    for r in results:
        param_value = get(r.params, param)

        if param_value not in parts:
            parts[param_value] = []

        parts[param_value].append(r)

    return parts

"""doc
Utility function for sorting results by fixing all parameters except one, and returning a list of results for all other values of the other parameter.
Takes the list of results to consider, a result whose parameter values you want to match, and the name of the parameter you want to sweep over.
Does not load results from disk.

```python
results = loadResults(exp, 'returns.npy')
result = next(results)
slice = sliceOverParameter(results, result, 'lambda')

print(slice) # => { 1.0: [Result, Result, ...], 0.99: [Result, Result, ...], 0.98: [Result, Result], ....}
```
"""
def sliceOverParameter(results: ResultList, slicer: BaseResult, param: str):
    parts = splitOverParameter(results, param)

    sl: Dict[str, Optional[BaseResult]] = {}
    for k in parts:
        sl[k] = find(parts[k], slicer, ignore=[param])

    return sl

Reducer = Callable[[np.ndarray], float]
"""doc
Returns the best result over a list of results.
Can defined "best" based on the `prefer` option; defaults to returning biggest result (e.g. biggest return).
Can also find best result over a range of a learning curve by specifying the last n steps with `steps=n` or the last p percent of steps with `percent=p`; defaults to returning mean over whole learning curve.
**Requires loading all results in list from disk.**

```python
results = loadResults(exp, 'returns.npy')

# get the largest return over the last 10% of steps
best = getBest(results, percent=0.1, prefer='big')
print(best.params) # -> { 'alpha': 1.0, 'lambda': 0.99 }

results = loadResults(exp, 'rmsve.npy')

# get the lowest rmsve over all steps
best = getBest(results)
print(best.params) # -> { 'alpha': 0.25, 'lambda': 1.0 }
```
"""
def getBest(results: ResultList, steps: Optional[int] = None, percent: float = 1.0, prefer: str = 'big', reducer: Optional[Reducer] = None):
    comparator = greater
    if prefer == 'small':
        comparator = lesser

    low = first(results)
    if steps is None:
        steps = len(low.mean())

    steps = int(steps * percent)

    if reducer is None:
        reducer = lambda arr: float(np.mean(arr))

    for r in results:
        a = r.mean()
        b = low.mean()
        am = reducer(a[0 - steps:])
        bm = reducer(b[0 - steps:])
        if np.isnan(bm) or comparator(am, bm):
            low = r

    return low

def greater(a: float, b: float):
    return a > b

def lesser(a: float, b: float):
    return a < b

"""doc
Find a specific result based on the metaParameters of another result.
Can optionally specify a list of parameters to ignore using for example `ignore=['alpha']`.
Will return the first result that matches.
Does not require loading results from disk.

```python
results = loadResults(exp, 'returns.npy')

result = next(results)
match = find(results, result, ignore=['lambda'])

print(result.params) # -> { 'alpha': 1.0, 'lambda': 1.0 }
print(match.params) # -> { 'alpha': 1.0, 'lambda': 0.98 }
```
"""
def find(stream: ResultList, other: BaseResult, ignore: List[str] = []):
    params = other.params
    for res in stream:
        if equal(params, res.params, ignore):
            return res

"""doc
Utility method for filtering results based on the value of each listed parameter.
If the listed parameter does not exist for some of the results (e.g. when comparing TD vs. GTD where TD does not have the second stepsize param), then those results will match True for the comparator.
Does not require loading results from disk.

```python
results = loadResults(exp, 'returns.npy')
results = whereParametersEqual(results, { 'alpha': 0.25 })

for res in results:
    print(res.params) # -> { 'alpha': 0.25, 'lambda': ... }
```
"""
def whereParametersEqual(results: ResultList, d: Dict[Any, Any]):
    return filter(lambda r: partialEqual(d, r.params), results)

"""doc
Utility method for filtering results based on the value of a particular parameter.
If the listed parameter does not exist for some of the results (e.g. when comparing TD vs. GTD where TD does not have the second stepsize param), then those results will match True for the comparator.
Does not require loading results from disk.

```python
results = loadResults(exp, 'returns.npy')
results = whereParameterGreaterEq(results, 'alpha', 0.25)

for res in results:
    print(res.params) # -> { 'alpha': 0.25, 'lambda': ... }, { 'alpha': 0.5, 'lambda': ... }, ...
```
"""
def whereParameterGreaterEq(results: ResultList, param: str, value: Any):
    return filter(lambda r: get(r.params, param, value) >= value, results)
