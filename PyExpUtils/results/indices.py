import os
from PyExpUtils.utils.archive import getArchiveName, inArchive
from PyExpUtils.results.paths import listResultsPaths

def listIndices(exp, runs=1):
    perms = exp.numPermutations()
    tasks = perms * runs
    return range(tasks)

def listMissingResults(exp, runs=1):
    idx = 0
    for path in listResultsPaths(exp, runs):
        archive = getArchiveName(path)
        if not os.path.exists(path) and not inArchive(archive, path):
            yield idx
        idx += 1
