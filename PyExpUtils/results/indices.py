import os
from PyExpUtils.utils.archive import getArchiveName, inArchive
from PyExpUtils.results.paths import listResultsPaths

"""doc
Returns an iterator over indices for each parameter permutation.
Can specify a number of runs and will cycle over the permutations `runs` number of times.

```python
for i in listIndices(exp, runs=2):
    print(i, exp.getRun(i)) # -> "0 0", "1 0", "2 0", ... "0 1", "1 1", ...
```
"""
def listIndices(exp, runs=1):
    perms = exp.numPermutations()
    tasks = perms * runs
    return range(tasks)

"""doc
Returns an iterator over indices which are missing results.
Detects if a results is missing by checking if the results folder exists, but cannot check the contents of the results folder.
If deeper checking is necessary, copy and modify the source of this function accordingly.

Useful for rescheduling jobs that were cancelled due to timeout (or randomly dropped jobs, etc.).
If no results are missing, then iterator is empty and the for loop is skipped.

```python
for i in listMissingResults(exp, runs=100):
    print(i) # -> 0, 1, 4, 23, 1002, ...
```
"""
def listMissingResults(exp, runs=1):
    idx = 0
    for path in listResultsPaths(exp, runs):
        archive = getArchiveName(path)
        if not os.path.exists(path) and not inArchive(archive, path):
            yield idx
        idx += 1
