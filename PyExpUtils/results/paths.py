import os

def listResultsPaths(exp, runs=1):
    perms = exp.permutations()
    tasks = perms * runs
    for i in range(tasks):
        yield exp.interpolateSavePath(i)

def listMissingResults(exp, runs=1):
    for path in listResultsPaths(exp, runs):
        if not os.path.exists(path):
            yield path
