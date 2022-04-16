from PyExpUtils.models.ExperimentDescription import ExperimentDescription

"""doc
Returns an iterator over indices for each parameter permutation.
Can specify a number of runs and will cycle over the permutations `runs` number of times.

```python
for i in listIndices(exp, runs=2):
    print(i, exp.getRun(i)) # -> "0 0", "1 0", "2 0", ... "0 1", "1 1", ...
```
"""
def listIndices(exp: ExperimentDescription, runs: int = 1):
    perms = exp.numPermutations()
    tasks = perms * runs
    return range(tasks)
