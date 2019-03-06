import os
from PyExpUtils.results.paths import listResultsPaths

def listIndices(exp, runs=1):
    perms = exp.permutations()
    tasks = perms * runs
    return range(tasks)

def listMissingResults(exp, runs=1):
    idx = 0
    for path in listResultsPaths(exp, runs):
        if not os.path.exists(path):
            yield idx
        idx += 1
